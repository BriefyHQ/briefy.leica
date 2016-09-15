"""Views to handle Jobs creation."""
from briefy.ws.resources import RESTService
from briefy.leica.models import Job
from briefy.ws import CORS_POLICY
from cornice.resource import resource


@resource(collection_path='/jobs', path='/jobs/{id}', cors_policy=CORS_POLICY)
class JobService(RESTService):
    """Jobs service."""

    model = Job
    friendly_name = model.__name__
    default_order_by = 'created_at'
