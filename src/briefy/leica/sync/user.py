"""Deal with user import."""
from briefy.common.utils.cache import timeout_cache
from briefy.leica import config
from briefy.leica import logger
from concurrent.futures import ThreadPoolExecutor

import briefy.knack as knack
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


@timeout_cache(300)
def login():
    """Use briefy.rolleiflex email login to get a valid token."""
    data = dict(username=config.API_USERNAME, password=config.API_PASSWORD)
    logger.debug('Login on rolleiflex to get a valid token.')
    response = requests.post(config.LOGIN_ENDPOINT, data=data, headers=get_headers())
    if response.status_code == 200:
        result = response.json()
        JwtAuth.token = result.get('token')
        JwtAuth.user = result.get('user')
    else:
        error = 'Login failed. Message: \n{msg}'.format(msg=response.text)
        logger.error(error)
        raise Exception(error)


@timeout_cache(300)
def get_rosetta() -> dict:
    """Get user map between Knack and Rolleiflex."""
    logger.debug('Requesting rosetta user mapping from Rolleiflex service.')
    response = requests.get(config.ROSETTA_ENDPOINT, headers=get_headers(), auth=JwtAuth())
    if response.status_code == 200:
        return response.json().get('data')
    else:
        error = 'Fail to get rosetta user mapping.'
        logger.error(error)
        raise Exception(error)


def print_update_user(future):
    """Print result of async user update."""
    print(future.result())


def update_user_briefy_id(profile='User'):
    """Find user brief_id and update back to knack."""
    rosetta = get_rosetta()
    user_model = knack.get_model(profile)
    all_users = user_model.query.all()

    with ThreadPoolExecutor(max_workers=10) as executor:
        print('Total of {0} users: {1}'.format(profile, len(all_users)))
        for user in all_users:
            briefy_id = rosetta.get(user.id)
            if user.briefy_id and user.briefy_id == briefy_id:
                continue
            elif briefy_id:
                user.briefy_id = briefy_id
                future = executor.submit(knack.commit_knack_object, user)
                future.add_done_callback(print_update_user)
            else:
                msg = 'User with email: {email} did not have briefy_id. Run Rolleiflex import.'
                print(msg.format(email=user.email))


def update_users():
    """Update briefy_id field for all user profiles using information from rosetta service."""
    user_profiles = (
        'User',
        'Photographer',
        'Client',
        'ProjectManager',
        'Qa',
        'ScoutingManager',
        'FinanceManager',
        'Supervisor',
        'AccountManager'
    )
    for profile in user_profiles:
        print('Update briefy_id for profile: {profile}'.format(profile=profile))
        update_user_briefy_id(profile)


if __name__ == '__main__':
    # update_user_briefy_id(profile='Photographer')
    update_users()
