"""Views to handle Customers creation."""
from briefy.leica.events import customer as events
from briefy.leica.models import Customer
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
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
    friendly_name = model.__name__
    default_order_by = 'title'
    filter_related_fields = [
        'customer_user', 'account_manager', 'business_contact.email', 'business_contact.fullname',
        'billing_contact.email', 'billing_contact.fullname'
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
    friendly_name = Customer.__name__
