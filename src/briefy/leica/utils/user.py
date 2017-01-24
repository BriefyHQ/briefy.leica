"""Utils to query user info."""
from briefy.common.utils.cache import timeout_cache
from briefy.leica.models.mixins import get_public_user_info


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
