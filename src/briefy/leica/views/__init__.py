"""Common view functions."""
from briefy.leica.models import UserProfile
from briefy.ws.resources.factory import BaseFactory
from pyramid.security import Allow
from pyramid.security import Everyone


class InternalFactory(BaseFactory):
    """Internal resource context factory."""

    model = None

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, Everyone, ['add', 'delete', 'edit', 'list', 'view'])
        ]
        return _acls


EMAIL_IN_USE_MESSAGE = 'This email is already associated with another user.'


def email_in_use(request):
    """Validate if email is used by another user.

    :param request: pyramid request.
    """
    email = request.json.get('email')
    user_id = request.json.get('id')
    db_user = UserProfile.query().filter_by(email=email).one_or_none()
    if db_user and not str(db_user.id) == user_id:
        return False
    else:
        return True
