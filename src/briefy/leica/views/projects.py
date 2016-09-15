"""Views to handle Projects creation."""
from briefy.ws.resources import RESTService
from briefy.leica.models import Project
from briefy.ws import CORS_POLICY
from cornice.resource import resource


@resource(collection_path='/projects', path='/projects/{id}', cors_policy=CORS_POLICY)
class ProjectService(RESTService):
    """Projects Service."""

    model = Project
    friendly_name = model.__name__
    default_order_by = 'created_at'

