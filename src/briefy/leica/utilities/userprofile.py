"""UserProfileData service."""
from briefy.common.log import logger
from briefy.common.users import SystemUser
from briefy.common.utilities.interfaces import IUserProfileQuery
from briefy.leica.models import UserProfile
from octopus.lens import AnyUUID
from octopus.lens import EasyUUID
from octopus.lens import map_from_object
from zope.interface import implementer

import sqlalchemy as sa


user_schema = {
    'id': '',
    'first_name': '',
    'last_name': '',
    'fullname': '$title',
    'email': '',
    'internal': False,
}


@implementer(IUserProfileQuery)
class LeicaUserProfileQuery:
    """Leica implementation of the IUserProfileQuery interface."""

    def get_data(self, user_id: AnyUUID) -> dict:
        """Get a map with user data."""
        try:
            user_id = EasyUUID(user_id)
        except ValueError:
            logger.warn(f'Invalid ACTOR UUID f{user_id}')
            data = user_schema.copy()
            data['id'] = str(user_id)
            data['fullname'] = ''
            return data

        if user_id == SystemUser.id:
            user = SystemUser
        else:
            user = UserProfile.get(user_id)

        return map_from_object(user_schema, user, default='') if user else {}

    def get_all_data(self, principal_ids: list) -> list:
        """Get all user data from a list of principals."""
        users = UserProfile.query().filter(UserProfile.id == sa.any_(principal_ids)).all()
        result = []
        for user in users:
            data = map_from_object(user_schema, user, default='')
            result.append(data)
        return result

    def update_wf_history(self, state_history: list) -> list:
        """Update workflow history with user data."""
        for item in state_history:
            user = item.get('actor', None)
            # first call when the actor value still a UUID string
            if isinstance(user, str):
                user_id = user
                new_actor = self.get_data(user_id)
                if new_actor:
                    item['actor'] = new_actor

        return state_history

    def apply_actors_info(self, data: dict, actors) -> dict:
        """Apply actors information for a given data dictionary.

        :param data: Data dictionary.
        :param actors: list of local roles to update user info
        :return: Data dictionary.
        """
        for local_role in actors:
            values = data.get(local_role, [])
            results = []
            for item in values:
                user_info = self.get_data(item) if item else None
                results.append(user_info)
            if results and values:
                data[local_role] = results
        return data


def get_user_profile_service():
    """Create a new instance of IUserProfileQuery service."""
    return LeicaUserProfileQuery()
