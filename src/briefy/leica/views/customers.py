"""Views to handle Projects creation."""
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.leica.models import Customer
from briefy.ws import CORS_POLICY
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
            (Allow, 'g:briefy_bizdev', ['add', 'delete', 'edit', 'list', 'view'])
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
    default_order_by = 'created_at'


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=CustomerFactory
)
class CustomerWorkflow(WorkflowAwareResource):
    """Customer workflow resource."""

    model = Customer
    friendly_name = Customer.__name__
