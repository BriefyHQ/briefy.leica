"""Views to handle Orders creation."""
from briefy.leica.events import order as events
from briefy.leica.models import Order
from briefy.ws import CORS_POLICY
from briefy.ws.resources import BaseResource
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from cornice.resource import view
from pyramid.httpexceptions import HTTPNotFound as NotFound
from pyramid.security import Allow

COLLECTION_PATH = '/orders'
PATH = COLLECTION_PATH + '/{id}'


class OrderFactory(BaseFactory):
    """Order context factory."""

    model = Order

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:customers', ['add', 'list', 'view'])
        ]
        return _acls


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=OrderFactory)
class OrderService(RESTService):
    """Orders service."""

    model = Order
    friendly_name = model.__name__
    default_order_by = 'created_at'
    filter_related_fields = [
        'project.title', 'project.id', 'project.status', 'location.locality', 'location.country',
        'location.fullname', 'location.formatted_address', 'customer.title',
    ]

    _default_notify_events = {
        'POST': events.OrderCreatedEvent,
        'PUT': events.OrderUpdatedEvent,
        'GET': events.OrderLoadedEvent,
        'DELETE': events.OrderDeletedEvent,
    }


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=OrderFactory
)
class OrderWorkflowService(WorkflowAwareResource):
    """Order workflow resource."""

    model = Order
    friendly_name = model.__name__


@resource(
    collection_path=PATH + '/versions',
    path=PATH + '/versions/{version_id}',
    cors_policy=CORS_POLICY,
    factory=OrderFactory
)
class OrderVersionsService(BaseResource):
    """Versioning of Orders."""

    model = Order
    friendly_name = model.__name__

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
