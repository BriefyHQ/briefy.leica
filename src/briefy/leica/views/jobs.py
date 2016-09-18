"""Views to handle Jobs creation."""
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.leica.models import Job
from briefy.ws import CORS_POLICY
from cornice.resource import resource


COLLECTION_PATH = '/jobs'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY)
class JobService(RESTService):
    """Jobs service."""

    model = Job
    friendly_name = model.__name__
    default_order_by = 'created_at'


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY
)
class JobWorkflow(WorkflowAwareResource):
    """Job workflow resource."""

    model = Job
    friendly_name = Job.__name__
