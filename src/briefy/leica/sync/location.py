"""Deal with address cleansing and creation."""
from briefy.leica import logger
from briefy.leica.sync import Auto
from briefy.leica.sync import PLACEHOLDERS
from briefy.knack.base import KnackEntity

import pycountry

# Initialize pycountry
TOTAL_COUNTRIES = len(pycountry.countries)  # noqa

CITY_MAPPING = (
    ('Amsterdam', 'Amsterdam', 'Netherlands'),
    ('Annecy', 'Annecy', 'France'),
    ('Bad Reichenhall', 'Bad Reichenhall', 'Germany'),
    ('Bali', 'Bali', 'Indonesia'),
    ('Bangkok', 'Bangkok', 'Thailand'),
    ('Benz-Usedom', 'Benz-Usedom', 'Germany'),
    ('Berlin', 'Berlin', 'Germany'),
    ('berlin', 'berlin', 'Germany'),
    ('Biarritz', 'Biarritz', 'France'),
    ('Birmingham', 'Birmingham', 'United Kingdom'),
    ('Braunschweig', 'Braunschweig', 'Germany'),
    ('Brühl', 'Brühl', 'Germany'),
    ('Denpasar', 'Denpasar', 'Indonesia'),
    ('Düsseldorf', 'Düsseldorf', 'Germany'),
    ('Edenkoben', 'Edenkoben', 'Germany'),
    ('Geelong', 'Geelong', 'Australia'),
    ('Glasgow', 'Glasgow', 'United Kingdom'),
    ('GLOUCESTERSHIRE', 'GLOUCESTERSHIRE', 'United Kingdom'),
    ('Goslar', 'Goslar', 'Germany'),
    ('Hannover', 'Hannover', 'Germany'),
    ('Hong Kong', 'Hong Kong', 'Hong Kong'),
    ('india', 'EMPTY_CITY', 'India'),
    ('Kassel', 'Kassel', 'Germany'),
    ('Köln (Porz)', 'Köln', 'Germany'),
    ('Leeds', 'Leeds', 'United Kingdom'),
    ('Leipzig', 'Leipzig', 'Germany'),
    ('Leverkusen', 'Leverkusen', 'Germany'),
    ('Lombok', 'Lombok', 'Indonesia'),
    ('Manchester', 'Manchester', 'United Kingdom'),
    ('Melbourne', 'Melbourne', 'Australia'),
    ('Munich', 'Munich', 'Germany'),
    ('Neustadt an der Donau', 'Neustadt an der Donau', 'Germany'),
    ('Newcastle upon Tyne', 'Newcastle upon Tyne', 'United Kingdom'),
    ('Osnabrück', 'Osnabrück', 'Germany'),
    ('Pattaya', 'Pattaya', 'Thailand'),
    ('Phuket', 'Phuket', 'Thailand'),
    ('Ravensburg', 'Ravensburg', 'Germany'),
    ('Regensburg', 'Regensburg', 'Germany'),
    ('San Francisco', 'San Francisco', 'United States'),
    ('San Jose', 'San Jose', 'United States'),
    ('Speyer', 'Speyer', 'Germany'),
    ('Stuttgart', 'Stuttgart', 'Germany'),
    ('Sydney', 'Sydney', 'Australia'),
    ('Torremolinos', 'Torremolinos', 'Spain'),
    ('Tours', 'Tours', 'France'),
    ('UK', PLACEHOLDERS['city'], 'United Kingdom'),
    ('Wiesbaden', 'Speyer', 'Germany'),
)

CITY_DICT = {i[0]: (i[1], i[2]) for i in CITY_MAPPING}

COUNTRY_MAPPING = {
    'Australia': ('Australia', 'AU'),
    'Austria': ('Austria', 'AT'),
    'Belarus': ('Belarus', 'BY'),
    'Croatia': ('Croatia', 'HZ'),
    'Curacao': ('Curaçao', 'CW'),
    'Czech Republic': ('Czechia', 'CZ'),
    'Denmark': ('Denmark', 'DK'),
    'Deutschland': ('Germany', 'DE'),
    'England': ('United Kingdom', 'UK'),
    'ES': ('Spain', 'ES'),
    'France': ('France', 'FR'),
    'Germany': ('Germany', 'DE'),
    'Iceland': ('Iceland', 'IS'),
    'ID': ('Indonesia', 'ID'),
    'Indo': ('Indonesia', 'ID'),
    'Indon': ('Indonesia', 'ID'),
    'Indonesia': ('Indonesia', 'ID'),
    'Indosnesia': ('Indonesia', 'ID'),
    'Ireland': ('Ireland', 'IE'),
    'Israel': ('Israel', 'IL'),
    'Italy': ('Italy', 'IT'),
    'Nederlands': ('Netherlands', 'NL'),
    'Netherlands': ('Netherlands', 'NL'),
    'Portugal': ('Portugal', 'PT'),
    'Republic of Singapore': ('Singapore', 'SG'),
    'Russia': ('Russian Federation', 'RU'),
    'Singapore': ('Singapore', 'SG'),
    'Spain': ('Spain', 'ES'),
    'Switzerland': ('Switzerland', 'CH'),
    'Taiwan': ('Viet Nam', 'VN'),
    'Thailand': ('Thailand', 'TH'),
    'The Netherlands': ('Netherlands', 'NL'),
    'U': ('United Kingdom', 'UK'),
    'UK': ('United Kingdom', 'UK'),
    'United Kingdom': ('United Kingdom', 'UK'),
    'United States': ('United States', 'US'),
    'Uruguay': ('Uruguay', 'UY'),
    'US': ('United States', 'US'),
    'USA': ('United States', 'US'),
    'Vietnam': ('Taiwan, Province of China', 'TW'),
    'Wales': ('United Kingdom', 'UK'),
}


def create_location_dict(address_field: str, kobj: KnackEntity, country: str='') -> dict:
    """Create location map based on any address field from a knack obj.

    :param address_field: address field name
    :param kobj: knack instance object
    :param country: Country hint.
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
    kcountry = klocation.country.strip() if klocation.country else ''
    street = klocation.street
    state = klocation.state.strip() if klocation.state else ''
    postcode = klocation.zip.strip() if klocation.zip else ''
    postcode = '0{postcode}'.format(postcode=postcode) if len(postcode) == 4 else postcode

    if kcountry:
        country = COUNTRY_MAPPING[kcountry][0] if kcountry in COUNTRY_MAPPING else kcountry

    if not klocation.city:
        city = PLACEHOLDERS['city']
    else:
        city = klocation.city.strip()

    # Deal with Job without address
    if postcode == '38100':
        street = 'Steinweg 20 ({street})'.format(street=street)
        city = 'Braunschweig'
        country = 'Germany'
    elif postcode == '49497':
        street = 'Markt 14 ({street})'.format(street=street)
        city = 'Mettingen'
        country = 'Germany'

    if city == PLACEHOLDERS['city'] and street:
        for key, tmp_city, tmp_country in CITY_MAPPING:
            if key in street:
                city = tmp_city
                country = tmp_country
                street = street.replace(city, '').replace(country, '')
                break
    elif city in CITY_DICT:
        country = CITY_DICT[city][1]

    country_iso = pycountry.countries.indices['name'].get(country, None)

    if country_iso:
        country_id = country_iso.alpha_2
        for piece in (city, country, postcode, state, 'ORTSTEIL', 'OT'):
            street = street.replace(piece, '').strip()

        parts = [
            street,
            city,
            state,
            postcode,
            country
        ]
        formatted_address = ', '.join(parts)
        info = dict(
            formatted_address=formatted_address,
            province=klocation.state,
            route=street,
            street_number='',
            country=country_id,
            postal_code=klocation.zip
        )

        return dict(
            country=country_id,
            formatted_address=formatted_address,
            info=info,
            locality=city.strip(' '),
            **extra_location_info
        )

    else:
        msg = 'Country not found: {country}, {city}, {street}. Field: {field}'.format(
            country=klocation.country,
            city=city,
            street=street,
            field=address_field
        )
        logger.info(msg)
        return {}
