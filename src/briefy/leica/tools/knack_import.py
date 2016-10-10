from briefy.leica import logger
from briefy.leica import config
from briefy.leica.db import Session  # noQA
from briefy.leica.db import create_engine
from briefy.leica.models import Customer as LCustomer
from briefy.leica.models import Job as LJob
from briefy.leica.models import JobLocation
from briefy.leica.models import Project as LProject
from briefy.common.vocabularies.categories import CategoryChoices
from stackfull import pop
from stackfull import push

import briefy.knack as K
import pycountry
import requests
import transaction
import uuid


# Initial workflow state based on field ['client_job_status']
knack_status_mapping = {
  'Job received': 'pending',
  'In scheduling process': 'scheduling',
  'Scheduled': 'scheduled',
  'In QA process': 'in_qa',
  'Completed': 'approved',
  'In revision ': 'revision',
  'Resolved': 'completed',
  'Cancelled ': 'cancelled'
}


def configure():
    """Bind session for 'stand alone' DB usage"""
    global Session
    engine = create_engine(config.DATABASE_URL, pool_recycle=3600)
    Session.configure(bind=engine)
    return Session

Session = configure()  # noQA


class JwtAuth(requests.auth.AuthBase):
    """Custom auth class to inject Authorization header from jwt token."""

    token = None
    user = None

    def __call__(self, request):
        """Customized authentication for briefy API request."""
        if not self.token:
            login()
        request.headers['Authorization'] = 'JWT {token}'.format(token=self.token)
        return request


def get_headers():
    """Default headers for all API requests."""
    headers = {'X-Locale': 'en_GB',
               'User-Agent': 'Briefy-SyncBot/0.1'}
    return headers


def login():
    """Use briefy.rolleiflex email login to get a valid token."""
    data = dict(username=config.API_USERNAME, password=config.API_PASSWORD)
    print('Login')
    response = requests.post(config.LOGIN_ENDPOINT, data=data, headers=get_headers())
    if response.status_code == 200:
        result = response.json()
        JwtAuth.token = result.get('token')
        JwtAuth.user = result.get('user')
    else:
        raise Exception('Login failed. Message: \n{msg}'.format(msg=response.text))


def get_model_and_data(model_name):
    """Load model and data dump from Knack"""
    logger.info('Retrieving {0} model from Knack'.format(model_name))
    model = K.get_model(model_name)
    logger.info('Querying all existing {0}s'.format(model_name))
    all_items = model.query.all()
    logger.info('Fetched {0} {1}s from Knack'.format(len(all_items), model_name))
    return model, all_items


class Auto:
    """Helper class to map dict to object."""

    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)

    def __getattr__(self, attr):
        return ''


def import_projects(session, rosetta: dict) -> dict:
    """Import all projects from knack and return a map of imported projects.

    :param session: sqlalchemy session object
    :param rosetta: map of knack user ID to briefy.rolleiflex UUID
    :return: dict with all projects imported
    """
    KProject, all_projects = get_model_and_data('Project')
    project_dict = {}
    customer_dict = {}
    count = 0
    for project in all_projects:
        if project.company[0]['id'] not in customer_dict:
            customer = LCustomer(external_id=project.company[0]['id'],
                                 title=project.company[0]['identifier'])
            session.add(customer)
            customer_dict[customer.external_id] = customer
        else:
            customer = customer_dict[project.company[0]['id']]
        session.add(customer)

        # TODO: add new field and import company_user from knack
        # customer_manager = company_user[0]['id']
        lproject = LProject(customer=customer,
                            external_id=project.id,
                            title=project.project_name.strip() or 'Undefined',
                            project_manager=rosetta.get(project.project_manager[0]['id']),
                            tech_requirements={'dimension': '4000x3000'})
        proj_id = lproject.id = uuid.uuid4()

        try:
            session.add(lproject)
            session.flush()
        except Exception as error:
            logger.error('Could not import project "{project}". Error {error}'.format(
                project=project.project_name,
                error=error))
            continue
        else:
            count += 1

        project_dict[project.id] = proj_id
    logger.info('{} new projects imported into Leica'.format(count))

    return project_dict


def create_location(location_dict: dict, job: LJob, session) -> JobLocation:
    """Create location based on knack job_location field.

    :param location_dict: job_location field
    :param job: briefy.leica job instance
    :param session: sqlalchemy session instance
    :return: job location instance
    """
    klocation = Auto(**location_dict)
    extra_location_info = {}
    if hasattr(klocation, 'latitude') and hasattr(klocation, 'longitude'):
        extra_location_info['coordinates'] = {
            'type': 'Point',
            'coordinates': [klocation.latitude, klocation.longitude]
        }
    country = klocation.country
    country = country.rstrip(' ')
    if country == 'USA':
        country = 'United States'
    country = pycountry.countries.indices['name'].get(country, None)
    if country:
        country_id = country.alpha2
        info = dict(
            province=klocation.state,
            route=klocation.street.strip('0123456789'),
            street_number=(pop()
                           if push(klocation.street and klocation.street.split()[-1]).isdigit()
                           else (pop(), '')[1]),
            # TODO: fix this in mapping for country abbreviation
            country=country_id,
            postal_code=klocation.zip
        )

        try:
            location = JobLocation(
                country=country_id,
                job_id=job.id,
                info=info,
                locality=klocation.city,
                **extra_location_info
            )
            session.add(location)
            session.flush()
        except Exception as error:
            msg = 'Failure to create location for Job: {job}. Error: {error}'
            logger.error(msg.format(job=job.customer_job_id, error=error))
            location = None
        return location

    else:
        msg = 'Country not found: {country}. Job ID: {job_id}. ' \
              'Customer ID: {customer_id}. Location: {location}'
        print(
            msg.format(
                country=klocation.country,
                customer_id=job.customer_job_id,
                job_id=job.job_id,
                location=location_dict,
            )
        )


def get_rosetta() -> dict:
    """Get user map between Knack and Rolleiflex"""
    response = requests.get(config.ROSETTA_ENDPOINT, headers=get_headers(), auth=JwtAuth())
    if response.status_code == 200:
        return response.json()
    else:
        logger.error('Fail to get rosetta user mapping.')
        return {}


def import_jobs(project_dict: dict, session: Session, rosetta: dict):
    """Import all jobs from knack.

    :param project_dict: map with all created projects.
    :param session: sqlalchemy session object
    :param rosetta: map of knack user ID to briefy.rolleiflex UUID
    :return: none
    """

    KJob, all_jobs = get_model_and_data('Job')
    count = 0
    for i, job in enumerate(all_jobs):
        # TODO: create a smart enum that can retrieve enum members by value:
        category = CategoryChoices.accommodation
        project_id = project_dict.get(job.project[0]['id'], None)
        if not project_id:
            logger.error('Could not import job {}: no corresponding project '.format(job.id))
            continue

        project = LProject.query().get(project_id)

        payload = dict(
            title=job.job_name or job.id,
            category=category,
            project=project,
            customer_job_id=job.job_id,
            job_id=job.internal_job_id or job.job_name or job.id,
            external_id=job.id,
            job_requirements=job.client_specific_requirement,
            assignment_date=job.assignment_date
        )

        if job.briefy_id:
            payload['id'] = job.briefy_id

        try:
            payload['professional_id'] = rosetta.get(job.responsible_photographer[0]['id'])
        except Exception:
            pass

        try:
            payload['qa_manager'] = rosetta.get(job.qa_manager[0]['id'])
        except Exception:
            pass

        try:
            payload['scout_manager'] = rosetta.get(job.scouting_manager[0]['id'])
        except Exception:
            pass

        try:
            ljob = LJob(**payload)
            session.add(ljob)
            session.flush()
            logger.debug(ljob.title)
        except Exception as error:
            msg = 'Could not instantiate SQLAlchemy job from {job}. Error: {error}'
            logger.error(msg.format(job=job.job_id, error=error))
            continue
        else:
            count += 1

        knack_status = list(job.client_job_status)
        if knack_status:
            status = knack_status_mapping.get(knack_status[0], 'in_qa')
        else:
            status = 'in_qa'

        logger.info('Job: {id}. knack status: {knack_status}, leica status: {status}'.format(
            id=ljob.id,
            knack_status=knack_status,
            status=status
        ))
        ljob.state = status
        if ljob.state_history and len(ljob.state_history) == 1:
            ljob.state_history[0]['message'] = 'Imported in this state from Knack database'
            ljob.state_history[0]['actor'] = 'g:system'
            ljob.state_history[0]['to'] = status

        location = create_location(job.__dict__['job_location'], ljob, session)
        if location:
            ljob.job_locations.append(location)

    logger.info('{0} new jobs imported into Leica'.format(count))


def main():
    """Handles all the stuff"""
    # Initialize pycountry
    len(pycountry.countries)
    rosetta = get_rosetta()

    with transaction.manager:
        project_dict = import_projects(Session, rosetta)
        # If the projects are already imported, the needed project_dictionary can
        # be queried with this
        # project_dict={p.external_id: p.id for p in LProject.query().all()  }
        import_jobs(project_dict, Session, rosetta)

if __name__ == '__main__':
    main()
