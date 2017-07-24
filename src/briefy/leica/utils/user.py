"""Utils to query user info."""
from briefy.common.config import ENV
from briefy.common.utilities.interfaces import IUserProfileQuery
from briefy.leica import models as m  # noQA
from briefy.leica.utils.rolleiflex import create_user
from briefy.leica.utils.rolleiflex import get_user
from briefy.leica.utils.rolleiflex import transition_user
from typing import Sequence
from zope.component import getUtility

import random
import string


def add_user_info_to_state_history(state_history):
    """Receive object state history and add user information.

    :param state_history: list of workflow state history.
    """
    profile_service = getUtility(IUserProfileQuery)
    return profile_service.update_wf_history(state_history)


def password_generator(size=8, chars=string.ascii_uppercase + string.digits):
    """Generate initial random user passwords."""
    password = ''.join(random.choice(chars) for _ in range(size))
    return password


def create_rolleiflex_user(profile, groups=()):
    """Create a new Rolleiflex user from a UserProfile."""
    initial_password = password_generator()
    return create_user(profile, initial_password, groups)


def activate_or_create_user(profile: 'm.UserProfile', groups: Sequence=()) -> bool:
    """Create an User on Rolleiflex or activate an existing User.

    :param profile: UserProfile to be synced to Rolleiflex.
    :param groups: Sequence of groups to be used on User creation
    :return: Status of this action.
    """
    user_id = profile.id
    user = get_user(user_id)
    if user:
        status = transition_user(user_id, 'activate')
    else:
        status = True if create_rolleiflex_user(profile, groups) else False
    return status


def _transition_profile(profile: 'm.UserProfile', transition: str) -> bool:
    """Transition an User connected to an UserProfile.

    :param profile: UserProfile to be transitioned on Rolleiflex.
    :param transition: Transition to be executed.
    :return: Status of this action
    """
    user_id = profile.id
    user = get_user(user_id)
    if user:
        status = transition_user(user_id, transition)
    else:
        # TODO: Raise exception here
        status = False
    return status


def activate_user(profile: 'm.UserProfile') -> bool:
    """Activate an User connected to an UserProfile.

    :param profile: UserProfile to be transitioned on Rolleiflex.
    :return: Status of this action
    """
    transition = 'activate'
    return _transition_profile(profile, transition)


def inactivate_user(profile: 'm.UserProfile') -> bool:
    """Inactivate an User connected to an UserProfile.

    :param profile: UserProfile to be transitioned on Rolleiflex.
    :return: Status of this action
    """
    transition = 'inactivate'
    return _transition_profile(profile, transition)
