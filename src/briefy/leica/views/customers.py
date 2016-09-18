"""Views to handle Projects creation."""
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.leica.models import Customer
from briefy.ws import CORS_POLICY
from cornice.resource import resource


COLLECTION_PATH = '/customers'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY)
class CustomersService(RESTService):
    """Customers Service."""

    model = Customer
    friendly_name = model.__name__
    default_order_by = 'created_at'


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY
)
class CustomerWorkflow(WorkflowAwareResource):
    """Customer workflow resource."""

    model = Customer
    friendly_name = Customer.__name__
