"""Utils to deal with Timezones.

Documentation: http://www.geonames.org/export/web-services.html
"""
import requests

ENDPOINT = 'http://api.geonames.org/timezoneJSON?formatted=true&lat={0}&lng={1}&username=briefy'


def timezone_from_coordinates(lat: float, lng: float) -> str:
    """Get timezone info from coordinates."""
    url = ENDPOINT.format(lat, lng)
    r = requests.get(url)
    data = r.json()
    if data and data.get('timezoneId'):
        return data['timezoneId']
    elif data.get('status', {}).get('value') == 19:
        # Rate limit
        raise RuntimeError('Too many requests')
