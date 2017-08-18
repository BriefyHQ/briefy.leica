"""Utils to query user info."""
from briefy.leica import models as m  # noQA
from briefy.leica import logger
from briefy.leica.config import ROLLEIFLEX_BASE
from briefy.leica.config import ROLLEIFLEX_USERNAME
from pyramid.httpexceptions import HTTPBadRequest
from typing import Optional
from typing import Sequence
from typing import Union
from uuid import UUID

import json
import requests


UUID_TYPE = Union[str, UUID]


ROLLEIFLEX_USER_CREATION = f'{ROLLEIFLEX_BASE}/users'
ROLLEIFLEX_LOGIN = f'{ROLLEIFLEX_BASE}/internal/login'
ROLLEIFLEX_USERS = f'{ROLLEIFLEX_BASE}/internal/users'

HEADERS = {
    'x-locale': 'en_GB',
    'content-type': 'application/json'
}


# TODO: Apply cache here
def _get_headers(authenticated: bool=False, username: str=ROLLEIFLEX_USERNAME) -> dict:
    """Return headers to be used for a call to Rolleiflex.

    :param authenticated: Header should contain authorization?
    :param username: Username to use with Authentication.
    :return: Dictionary containing header for connection.
    """
    headers = HEADERS.copy()
    if authenticated:
        payload = json.dumps({'username': username})
        request = requests.post(ROLLEIFLEX_LOGIN, headers=headers, data=payload)
        if request.status_code not in (200, 201):
            body = request.content
            raise ValueError(f'Rolleiflex authentication failed. Result: {body}')
        data = request.json()
        token = data['token']
        headers['Authorization'] = f'JWT {token}'
    return headers


def get_user(user_id: UUID_TYPE) -> Optional[dict]:
    """Giver an user_id, return the payload from Rolleiflex, or None.

    :param user_id: ID of the user
    :return: User payload or None
    """
    headers = _get_headers(authenticated=True)
    endpoint = f'{ROLLEIFLEX_USERS}/{user_id}'
    response = requests.get(endpoint, headers=headers)
    if response.status_code in (200, 201):
        data = response.json()
        return data


def transition_user(user_id: UUID_TYPE, transition: str) -> bool:
    """Execute a transition on an User with a given user_id.

    :param user_id: ID of the user
    :return: If transition was successful or not
    """
    headers = _get_headers(authenticated=True)
    endpoint = f'{ROLLEIFLEX_USERS}/{user_id}/transitions'
    payload = json.dumps(
        {
            'transition': transition,
            'message': 'Transitioned by Leica',
        }
    )
    response = requests.post(endpoint, data=payload, headers=headers)
    status = True if response.status_code in (200, 201) else False
    return status


def create_user(profile: 'm.UserProfile', initial_password: str, groups: Sequence) -> dict:
    """Create an user on Rolleiflex.

    :param profile: User profile to create on Rolleiflex.
    :param initial_password: Password for the user.
    :param groups: List of groups this user will be part of
    :return: Response from Rolleiflex.
    """
    headers = _get_headers()
    groups = [{'name': value for value in groups}]
    payload = json.dumps({
        'id': str(profile.id),
        'email': profile.email,
        'first_name': profile.first_name,
        'last_name': profile.last_name,
        'password': initial_password,
        'locale': 'en_GB',
        'groups': groups,
    })

    response = requests.post(ROLLEIFLEX_USER_CREATION, data=payload, headers=headers)
    if response.status_code in (200, 201):
        logger.info(f'Success user creation. Email: {profile.email}.')
        # We put this here to be serialized to sqs
        profile.initial_password = initial_password
        return response.json()
    else:
        try:
            result = response.json()
        except Exception as exc:
            msg = f'Failure to create user on Rolleiflex. Exception: {exc}'
        else:
            default_msg = 'Error message not found. Failure to create user on Rolleiflex.'
            msg = result.get('message', default_msg)

        logger.error(msg)
        # TODO: improve exception handling
        raise HTTPBadRequest(msg)
