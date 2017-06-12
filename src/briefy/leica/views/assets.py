"""Views to handle Assets creation."""
from briefy.leica.events import asset as events
from briefy.leica.models import Image
from briefy.ws import CORS_POLICY
from briefy.ws.resources import HistoryService
from briefy.ws.resources import RESTService
from briefy.ws.resources import VersionsService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


COLLECTION_PATH = '/assignments/{assignment_id}/assets'
PATH = COLLECTION_PATH + '/{id}'


class AssetFactory(BaseFactory):
    """Asset context factory."""

    # model = Asset
    # For now all assets will be images
    model = Image

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

    model = Image
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
        # Remove assignment_id
        allowed_fields.remove('assignment_id')
        return allowed_fields

    def default_filters(self, query) -> object:
        """Default filters for this Service."""
        assignment_id = self.request.matchdict.get('assignment_id')
        if assignment_id:
            query.filter(self.model.assignment_id == assignment_id)
        return query


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=AssetFactory
)
class AssetWorkflow(WorkflowAwareResource):
    """Assets workflow resource."""

    model = Image


@resource(
    collection_path=PATH + '/versions',
    path=PATH + '/versions/{version_id}',
    cors_policy=CORS_POLICY,
    factory=AssetFactory
)
class AssetVersions(VersionsService):
    """Versions of assets."""

    model = Image


@resource(
    path=PATH + '/history',
    cors_policy=CORS_POLICY,
    factory=AssetFactory
)
class AssetHistory(HistoryService):
    """Workflow history of assets."""

    model = Image
