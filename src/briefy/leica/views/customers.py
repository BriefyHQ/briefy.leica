"""Views to handle Customers creation."""
from briefy.leica.events import customer as events
from briefy.leica.models import Customer
from briefy.ws import CORS_POLICY
from briefy.ws.resources import HistoryService
from briefy.ws.resources import RESTService
from briefy.ws.resources import VersionsService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


COLLECTION_PATH = '/customers'
PATH = COLLECTION_PATH + '/{id}'


class CustomerFactory(BaseFactory):
    """Customer context factory."""

    model = Customer

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:briefy_bizdev', ['list', 'view']),
            (Allow, 'g:customers', ['list', 'view'])
        ]
        return _acls


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=CustomerFactory)
class CustomersService(RESTService):
    """Customers Service."""

    model = Customer
    default_order_by = 'title'
    filter_related_fields = [
        'customer_users', 'internal_account', 'business_contact.email',
        'business_contact.fullname', 'billing_contact.email', 'billing_contact.fullname',
        'legal_name', 'tax_country', 'billing_info.title'
    ]

    _default_notify_events = {
        'POST': events.CustomerCreatedEvent,
        'PUT': events.CustomerUpdatedEvent,
        'GET': events.CustomerLoadedEvent,
        'DELETE': events.CustomerDeletedEvent,
    }


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=CustomerFactory
)
class CustomerWorkflowService(WorkflowAwareResource):
    """Customer workflow resource."""

    model = Customer


@resource(
    collection_path=PATH + '/versions',
    path=PATH + '/versions/{version_id}',
    cors_policy=CORS_POLICY,
    factory=CustomerFactory
)
class CustomerVersionsService(VersionsService):
    """Versioning of Customers."""

    model = Customer
    default_order_by = 'title'


@resource(
    collection_path=PATH + '/history',
    path=PATH + '/history/{item_id}',
    cors_policy=CORS_POLICY,
    factory=CustomerFactory
)
class CustomerHistory(HistoryService):
    """Workflow history of Customers."""

    model = Customer
