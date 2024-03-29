"""Views to handle User Profile management."""
from briefy.leica.events import userprofile as events
from briefy.leica.models import CustomerUserProfile
from briefy.leica.models import InternalUserProfile
from briefy.leica.models import UserProfile
from briefy.leica.views import email_in_use
from briefy.leica.views import EMAIL_IN_USE_MESSAGE
from briefy.ws import CORS_POLICY
from briefy.ws.resources import HistoryService
from briefy.ws.resources import RESTService
from briefy.ws.resources import VersionsService
from briefy.ws.resources import WorkflowAwareResource
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
    default_order_by = 'title'
    filter_related_fields = [
        'title',
        'customer_roles.entity_id',
        'project_roles.entity_id'
    ]

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


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=CustomerProfileFactory
)
class CustomerProfileWorkflowService(WorkflowAwareResource):
    """CustomerUserProfile workflow resource."""

    model = CustomerUserProfile


@resource(
    collection_path=PATH + '/versions',
    path=PATH + '/versions/{version_id}',
    cors_policy=CORS_POLICY,
    factory=CustomerProfileFactory
)
class CustomerProfileVersionsService(VersionsService):
    """Versioning of CustomerProfiles."""

    model = CustomerUserProfile


@resource(
    collection_path=PATH + '/history',
    path=PATH + '/history/{item_id}',
    cors_policy=CORS_POLICY,
    factory=CustomerProfileFactory
)
class CustomerProfileHistory(HistoryService):
    """Workflow history of CustomerProfiles."""

    model = CustomerUserProfile


class InternalProfileFactory(BaseFactory):
    """InternalProfile context factory."""

    model = InternalUserProfile

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

    model = InternalUserProfile
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


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=InternalProfileFactory
)
class InternalProfileWorkflowService(WorkflowAwareResource):
    """InternalProfile workflow resource."""

    model = InternalUserProfile


@resource(
    collection_path=PATH + '/versions',
    path=PATH + '/versions/{version_id}',
    cors_policy=CORS_POLICY,
    factory=InternalProfileFactory
)
class InternalProfileVersionsService(VersionsService):
    """Versioning of InternalProfiles."""

    model = InternalUserProfile


@resource(
    collection_path=PATH + '/history',
    path=PATH + '/history/{item_id}',
    cors_policy=CORS_POLICY,
    factory=InternalProfileFactory
)
class InternalProfileHistory(HistoryService):
    """Workflow history of InternalProfiles."""

    model = InternalUserProfile
