"""Views to handle Assets creation."""
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.leica.models import Asset
from briefy.leica.models import Job
from briefy.ws import CORS_POLICY
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


COLLECTION_PATH = '/jobs/{job_id}/assets'
PATH = COLLECTION_PATH + '/{id}'


class AssetFactory(BaseFactory):
    """Asset context factory."""

    model = Asset

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.
        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:briefy_qa', ['add', 'delete', 'edit', 'list', 'view'])
        ]
        return _acls


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=AssetFactory)
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


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=AssetFactory
)
class AssetWorkflow(WorkflowAwareResource):
    """Assets workflow resourve."""

    model = Asset
    friendly_name = Asset.__name__
