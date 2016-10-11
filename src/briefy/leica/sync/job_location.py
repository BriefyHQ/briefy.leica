from briefy.leica import logger
from briefy.leica.sync import Auto
from briefy.leica.models import Job
from briefy.leica.models import JobLocation
from stackfull import pop
from stackfull import push

import pycountry

# Initialize pycountry
TOTAL_COUNTRIES = len(pycountry.countries)  # noqa


def create_location(location_dict: dict, job: Job, session) -> JobLocation:
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
