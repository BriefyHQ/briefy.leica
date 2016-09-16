"""Views to handle Assets creation."""
from briefy.ws.resources import RESTService
from briefy.leica.models import Asset
from briefy.leica.models import Job
from briefy.ws import CORS_POLICY
from cornice.resource import resource


@resource(
    collection_path='/jobs/{job_id}/assets',
    path='/jobs/{job_id}/assets/{id}',
    cors_policy=CORS_POLICY
)
class AssetService(RESTService):
    """Assets service."""

    model = Asset
    friendly_name = Asset.__name__
    default_order_by = 'created_at'

    @property
    def filter_allowed_fields(self):
        """List of fields allowed in filtering and sorting."""
        allowed_fields = super().filter_allowed_fields
        # Remove job_id
        allowed_fields.remove('job_id')
        return allowed_fields

    @property
    def default_filters(self) -> tuple:
        """Default filters for this Service."""
        job_id = self.request.matchdict.get('job_id', '')
        filters = list(super().default_filters)
        filters.append((Job.id == job_id))
        return tuple(filters)
