"""Utils to deal with Timezones.

Documentation: http://www.geonames.org/export/web-services.html
"""
from briefy.leica import logger

import requests


ENDPOINT = 'http://api.geonames.org/timezoneJSON?formatted=true&lat={0}&lng={1}&username=briefy'


def timezone_from_coordinates(lat: float, lng: float) -> str:
    """Get timezone info from coordinates."""
    url = ENDPOINT.format(lat, lng)
    data = None
    try:
        r = requests.get(url)
        data = r.json()
        if data and data.get('timezoneId'):
            return data['timezoneId']
        elif data.get('status', {}).get('value') == 19:
            # Rate limit
            logger.error(
                'Unable to fetch timezone: GeoNames rate limit.'
            )
        else:
            logger.error(
                'Unable to fetch timezone thanks to GeoNames throttling '
            )
    except Exception as exc:
        logger.exception(
            'Error retrieving timezone info: ' + str(exc)
        )
