"""Views to handle Projects creation."""
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.leica.models import Project
from briefy.ws import CORS_POLICY
from cornice.resource import resource


COLLECTION_PATH = '/projects'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY)
class ProjectService(RESTService):
    """Projects Service."""

    model = Project
    friendly_name = model.__name__
    default_order_by = 'created_at'


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY
)
class ProjectWorkflow(WorkflowAwareResource):
    """Project workflow resource."""

    model = Project
    friendly_name = Project.__name__
