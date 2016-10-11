from briefy.leica import config
from briefy.leica import logger

import requests


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


def get_rosetta() -> dict:
    """Get user map between Knack and Rolleiflex"""
    response = requests.get(config.ROSETTA_ENDPOINT, headers=get_headers(), auth=JwtAuth())
    if response.status_code == 200:
        return response.json()
    else:
        logger.error('Fail to get rosetta user mapping.')
        return {}
