"""Views to handle User Profile management."""
from briefy.leica.events import userprofile as events
from briefy.leica.models import UserProfile
from briefy.leica.models import CustomerUserProfile
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow

COLLECTION_PATH = '/profiles/me'
PATH = COLLECTION_PATH + '/{id}'


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

    _default_notify_events = {
        'POST': events.UserProfileCreatedEvent,
        'PUT': events.UserProfileUpdatedEvent,
        'GET': events.UserProfileLoadedEvent,
        'DELETE': events.UserProfileDeletedEvent,
    }


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

    _default_notify_events = {
        'POST': events.UserProfileCreatedEvent,
        'PUT': events.UserProfileUpdatedEvent,
        'GET': events.UserProfileLoadedEvent,
        'DELETE': events.UserProfileDeletedEvent,
    }
