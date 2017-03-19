"""Views to handle User Profile management."""
from briefy.leica.events import userprofile as events
from briefy.leica.models import UserProfile
from briefy.leica.models import BriefyUserProfile
from briefy.leica.models import CustomerUserProfile
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow

COLLECTION_PATH = '/profiles/me'
PATH = COLLECTION_PATH + '/{id}'

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


class ProfileFactory(BaseFactory):
    """UserProfile context factory."""

    model = UserProfile

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:briefy', ['edit', 'view']),
            (Allow, 'g:professionals', ['edit', 'view']),
            (Allow, 'g:customers', ['edit', 'view']),
            (Allow, 'g:briefy_tech', ['create', 'delete', 'edit', 'list', 'view']),
            (Allow, 'g:briefy_bizdev', ['create', 'edit', 'list', 'view']),
            (Allow, 'g:briefy_pm', ['create', 'edit', 'list', 'view']),
            (Allow, 'g:briefy_tech', ['create', 'delete', 'edit', 'list', 'view']),
        ]
        return _acls


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=ProfileFactory)
class ProfileService(RESTService):
    """CustomerUserProfile Service."""

    model = UserProfile
    friendly_name = model.__name__
    default_order_by = 'title'
    filter_related_fields = ['title']

    _validators = (
        ('GET', ('validate_id', )),
        ('PUT', ('validate_id', )),
        ('POST', ('email_in_use', ))
    )

    _default_notify_events = {
        'POST': events.UserProfileCreatedEvent,
        'PUT': events.UserProfileUpdatedEvent,
        'GET': events.UserProfileLoadedEvent,
        'DELETE': events.UserProfileDeletedEvent,
    }

    def email_in_use(self, request):
        """Email validation."""
        if not email_in_use(request):
            self.raise_invalid(name='email', description=EMAIL_IN_USE_MESSAGE)


class CustomerProfileFactory(BaseFactory):
    """CustomerProfile context factory."""

    model = CustomerUserProfile

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:briefy', ['edit', 'view']),
            (Allow, 'g:professionals', ['edit', 'view']),
            (Allow, 'g:customers', ['edit', 'view']),
            (Allow, 'g:briefy_tech', ['create', 'delete', 'edit', 'list', 'view']),
            (Allow, 'g:briefy_bizdev', ['create', 'edit', 'list', 'view']),
            (Allow, 'g:briefy_pm', ['create', 'edit', 'list', 'view']),
            (Allow, 'g:briefy_tech', ['create', 'delete', 'edit', 'list', 'view']),
        ]
        return _acls


COLLECTION_PATH = '/profiles/customer'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=CustomerProfileFactory)
class CustomerProfileService(RESTService):
    """CustomerUserProfile Service."""

    model = CustomerUserProfile
    friendly_name = model.__name__
    default_order_by = 'title'
    filter_related_fields = ['title']

    _validators = (
        ('GET', ('validate_id', )),
        ('PUT', ('validate_id', )),
        ('POST', ('email_in_use', ))
    )

    _default_notify_events = {
        'POST': events.UserProfileCreatedEvent,
        'PUT': events.UserProfileUpdatedEvent,
        'GET': events.UserProfileLoadedEvent,
        'DELETE': events.UserProfileDeletedEvent,
    }

    def email_in_use(self, request):
        """Email validation."""
        if not email_in_use(request):
            self.raise_invalid(name='email', description=EMAIL_IN_USE_MESSAGE)


class InternalProfileFactory(BaseFactory):
    """InternalProfile context factory."""

    model = BriefyUserProfile

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:briefy_tech', ['create', 'delete', 'edit', 'list', 'view']),
        ]
        return _acls


COLLECTION_PATH = '/profiles/internal'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=InternalProfileFactory)
class InternalProfileService(RESTService):
    """InternalUserProfile Service."""

    model = BriefyUserProfile
    friendly_name = model.__name__
    default_order_by = 'title'
    filter_related_fields = ['title']

    _validators = (
        ('GET', ('validate_id', )),
        ('PUT', ('validate_id', )),
        ('POST', ('email_in_use', ))
    )

    _default_notify_events = {
        'POST': events.UserProfileCreatedEvent,
        'PUT': events.UserProfileUpdatedEvent,
        'GET': events.UserProfileLoadedEvent,
        'DELETE': events.UserProfileDeletedEvent,
    }

    def email_in_use(self, request):
        """Email validation."""
        if not email_in_use(request):
            self.raise_invalid(name='email', description=EMAIL_IN_USE_MESSAGE)
