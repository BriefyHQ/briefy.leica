"""Views to handle Assets creation."""
from briefy.leica.events import asset as events
from briefy.leica.models import Asset
from briefy.ws import CORS_POLICY
from briefy.ws.resources import BaseResource
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from cornice.resource import view
from pyramid.httpexceptions import HTTPNotFound as NotFound
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
    items_per_page = 150
    default_order_by = 'created_at'

    _default_notify_events = {
        'POST': events.AssetCreatedEvent,
        'PUT': events.AssetUpdatedEvent,
        'GET': events.AssetLoadedEvent,
        'DELETE': events.AssetDeletedEvent,
    }

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
        job_id = self.request.matchdict.get('job_id')
        filters = list(super().default_filters)
        if job_id:
            filters.append((Asset.job_id == job_id))
        return tuple(filters)


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=AssetFactory
)
class AssetWorkflow(WorkflowAwareResource):
    """Assets workflow resource."""

    model = Asset
    friendly_name = Asset.__name__


@resource(
    collection_path=PATH + '/versions',
    path=PATH + '/versions/{version_id}',
    cors_policy=CORS_POLICY,
    factory=AssetFactory
)
class AssetVersions(BaseResource):
    """Versioning of assets."""

    model = Asset
    friendly_name = Asset.__name__

    @view(validators='_run_validators')
    def collection_get(self):
        """Return the list of versions for this object."""
        id = self.request.matchdict.get('id', '')
        obj = self.get_one(id)
        raw_versions = obj.versions
        versions = []
        for version_id, version in enumerate(raw_versions):
            versions.append(
                {
                    'id': version_id,
                    'updated_at': version.updated_at
                }
            )
        response = {
            'versions': versions,
            'total': obj.version + 1
        }
        return response

    @view(validators='_run_validators')
    def get(self):
        """Return a version for this object."""
        id = self.request.matchdict.get('id', '')
        obj = self.get_one(id)
        version_id = self.request.matchdict.get('version_id', 0)
        try:
            version_id = int(version_id)
            version = obj.versions[version_id]
        except (ValueError, IndexError):
            raise NotFound(
                '{friendly_name} with version: {id} not found.'.format(
                    friendly_name=self.friendly_name,
                    id=version_id
                )
            )
        return version
