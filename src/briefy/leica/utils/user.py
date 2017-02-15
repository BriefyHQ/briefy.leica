"""Utils to query user info."""
from briefy.leica import logger
from briefy.leica.config import API_BASE
from briefy.leica.models.mixins import get_public_user_info
from pyramid.httpexceptions import HTTPBadRequest

import json
import random
import requests
import string


def add_user_info_to_state_history(state_history):
    """Receive object state history and add user information.

    :param state_history: list of workflow state history.
    """
    for item in state_history:
        user = item.get('actor', None)
        if isinstance(user, str):
            user_id = user  # first call where actor is a UUID string
            new_actor = get_public_user_info(user_id)
            if new_actor:
                item['actor'] = new_actor


def password_generator(size=8, chars=string.ascii_uppercase + string.digits):
    """Generate initial random user passwords."""
    password = ''.join(random.choice(chars) for _ in range(size))
    return password


def create_rolleiflex_user(profile, groups=()):
    """Create a new Rolleiflex user from a UserProfile."""
    # add a rolleiflex user
    url = API_BASE + '/users'
    groups = [{'name': value for value in groups}]
    initial_password = password_generator()
    payload = dict(
        id=str(profile.id),
        email=profile.email,
        first_name=profile.first_name,
        last_name=profile.last_name,
        password=initial_password,
        locale='en_GB',
        groups=groups,
    )

    headers = {
        'x-locale': "en_GB",
        'content-type': "application/json"
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    if response.status_code in (200, 201):
        logger.info('Success user creation. Email: {email}.'.format(email=profile.email))
        # We put this here to be serialized to sqs
        profile.initial_password = initial_password
        return response.json()
    else:
        try:
            result = response.json()
        except Exception as exc:
            msg = 'Failure to create user on Rolleiflex. Exception: {exc}'.format(exc=exc)
        else:
            default_msg = 'Error message not found. Failure to create user on Rolleiflex.'
            msg = result.get('message', default_msg)

        logger.error(msg)
        # TODO: improve exception handling
        raise HTTPBadRequest(msg)
