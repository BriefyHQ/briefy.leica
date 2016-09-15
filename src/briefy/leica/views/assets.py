"""Views to handle Assets creation."""
from briefy.ws.resources import RESTService
from briefy.leica.models import Asset
from briefy.ws import CORS_POLICY
from cornice.resource import resource


@resource(collection_path='/assets', path='/assets/{id}', cors_policy=CORS_POLICY)
class AssetService(RESTService):
    """Assets service."""

    model = Asset
    friendly_name = Asset.__name__
    default_order_by = 'created_at'
