from briefy.leica import logger
from briefy.leica.config import DATABASE_URL
from briefy.leica.db import Session  # noQA
from briefy.leica.db import create_engine
from briefy.leica.models import Customer as LCustomer
from briefy.leica.models import Job as LJob
from briefy.leica.models import JobLocation
from briefy.leica.models import Project as LProject
from briefy.leica.models.types import CategoryChoices
import briefy.knack as K
from stackfull import push, pop

import logging
import pycountry
import transaction
import uuid

logger.setLevel(logging.DEBUG)
logger.handlers[0].setLevel(logging.DEBUG)


# Initial workflow state based on field ['client_job_status']
knack_status_mapping = {
  'Job received': 'pending',
  'In scheduling process': 'scheduling',
  'Scheduled': 'scheduled',
  'In QA process': 'in_qa',
  'Completed': 'approved',
  'In revision ': 'revision',
  'Resolved': 'completed',
  'Cancelled ':'cancelled'
}


def configure():
    """Bind session for 'stand alone' DB usage"""
    global Session
    engine = create_engine(DATABASE_URL, pool_recycle=3600)
    Session.configure(bind=engine)
    return Session

Session = configure()  # noQA


def get_model_and_data(model_name):
    """Load model and data dump from Knack"""
    logger.info('Retrieving {0} model from Knack'.format(model_name))
    model = K.get_model(model_name)
    logger.info('Querying all existing {0}s'.format(model_name))
    all_items = model.query.all()
    logger.info('Fetched {0} {1}s from Knack'.format(len(all_items), model_name))
    return model, all_items


class Auto:
    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)
    def __getattr__(self, attr):
        return ''


def import_projects():

    KProject, all_projects = get_model_and_data('Project')
    project_dict = {}
    customer_dict = {}
    count = 0
    for project in all_projects:
        if project.company[0]['id'] not in customer_dict:
            customer = LCustomer(external_id=project.company[0]['id'],
                                 title=project.company[0]['identifier'])
            Session.add(customer)
            customer_dict[customer.external_id] = customer
        else:
            customer = customer_dict[project.company[0]['id']]
        Session.add(customer)

        lproject = LProject(customer=customer, external_id=project.id,
                            title=project.project_name.strip() or 'Undefined',
                            tech_requirements={'dimension': '4000x3000'})
        proj_id = lproject.id = uuid.uuid4()

        with transaction.manager:
            try:
                Session.add(lproject)
                Session.flush()
            except Exception as error:
                logging.error('Could not import project "{}". Error {}'.format(
                    project.project_name, error))
                Session.rollback()
                continue

            count += 1
        project_dict[project.id] = proj_id
    logging.info('{} new projects imported into Leica'.format(count))

    return project_dict


def create_location(location_dict):
        klocation = Auto(**location_dict)
        extra_location_info = {}
        if hasattr(klocation, 'latitude') and hasattr(klocation, 'longitude'):
            extra_location_info['coordinates'] = {
                'type': 'Point',
                'coordinates': [klocation.latitude, klocation.longitude]
            }
        country = pycountry.countries.indices['name'].get(klocation.country, None)
        if country:
            country_id = country.alpha2
        else:
            country_id = None
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

        location = JobLocation(
            country=country_id,
            info=info,
            locality=klocation.city,
            **extra_location_info
        )
        return location


def import_jobs(project_dict):

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

        location = create_location(job.__dict__['job_location'])
        Session.add(location)

        try:
            ljob = LJob(
                title=job.job_name or job.id,
                category=category,
                project=project,
                customer_job_id=job.job_id,
                job_id=job.job_id or job.job_name or job.id,
                external_id=job.id,

                job_requirements=job.client_specific_requirement,
                assignment_date = job.assignment_date,

                # TODO right now, this is knack id:
                # professional=job.responsible_photographer[0]['id'],
                # TODO: FIX
                # project_manager= project.manager
                # TODO: FIX
                # qa_manager=job.qa_manager[0]['id']
                # TODO: FIX
                # scout_manager=,
                # TODO: FIX
                # finance_manager=,
            )
        except Exception as error:
            logger.error('SNAFU: Could not instantiate SQLAlchemy job from {0}'.format(job))
            continue

        if job.client_job_status:
            status = knack_status_mapping.get(job.client_job_status.pop(), 'in_qa')
        else:
            # For purposes of inital import into LEICA only:
            status = 'in_qa'

        ljob.state = knack_status_mapping.get(status, 'in_qa')
        if ljob.state_history and len(ljob.state_history) == 1:
            ljob.state_history[0]['message'] = 'Imported in this state from Knack database'

        ljob.job_locations.append(location)
        #if job.set_price:
            #ljob.price = int(job.set_price)
        if job.briefy_id:
            ljob.id = job.briefy_id

        with transaction.manager:
            try:
                Session.add(ljob)
                Session.flush()
                logger.debug(ljob.title)
            except Exception as error:
                logging.error('Could not import job "{}". Error {}'.format(ljob.title, error))
                Session.rollback()
                continue

            count += 1

    logging.info('{0} new jobs imported into Leica'.format(count))


def main():
    """Handles all the stuff"""
    # Initialize pycountry
    len(pycountry.countries)

    project_dict = import_projects()
    # If the projects are already imported, the needed project_dictionary can
    # be queried with this
    # project_dict={p.external_id: p.id for p in LProject.query().all()  }
    import_jobs(project_dict)

if __name__ == '__main__':
    main()
