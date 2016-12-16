from briefy.leica import logger
from briefy.leica.sync import Auto
from briefy.knack.base import KnackEntity
from stackfull import pop
from stackfull import push

import pycountry

# Initialize pycountry
TOTAL_COUNTRIES = len(pycountry.countries)  # noqa


def create_location_dict(address_field: str, kobj: KnackEntity) -> dict:
    """Create location map based on any address field from a knack obj.

    :param address_field: address field name
    :param kobj: knack instance object
    :return: location dict
    """
    location_dict = kobj.__dict__[address_field]
    if not location_dict:
        return {}
    klocation = Auto(**location_dict)
    extra_location_info = {}
    if hasattr(klocation, 'latitude') and hasattr(klocation, 'longitude'):
        extra_location_info['coordinates'] = {
            'type': 'Point',
            'coordinates': [klocation.latitude, klocation.longitude]
        }
    country = klocation.country
    country = country.rstrip(' ')

    if not klocation.city:
        city = 'EMPTY_CITY'
    else:
        city = klocation.city

    if country == 'USA':
        country = 'United States'
    elif country == 'UK':
        country = 'United Kingdom'
    elif country == 'Deutschland':
        country = 'Germany'
    elif country == 'The Netherlands':
        country = 'Netherlands'

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

        return dict(
            country=country_id,
            info=info,
            locality=city,
            **extra_location_info
        )

    else:
        msg = 'Country not found: {country}. Field: {field}'
        msg = msg.format(country=klocation.country, field=address_field)
        print(msg)
        logger.info(msg)
        return {}
