"""Views to handle Pools creation."""
from briefy.leica.events import pool as events
from briefy.leica.models import Pool
from briefy.ws import CORS_POLICY
from briefy.ws.resources import HistoryService
from briefy.ws.resources import RESTService
from briefy.ws.resources import VersionsService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


COLLECTION_PATH = '/pools'
PATH = COLLECTION_PATH + '/{id}'


class PoolFactory(BaseFactory):
    """Pool context factory."""

    model = Pool

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:briefy_pm', ['add', 'delete', 'edit', 'list', 'view']),
            (Allow, 'g:briefy_scout', ['add', 'delete', 'edit', 'list', 'view'])
        ]
        return _acls


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=PoolFactory)
class PoolService(RESTService):
    """Pool service."""

    model = Pool
    default_order_by = 'title'
    filter_related_fields = []

    _default_notify_events = {
        'POST': events.PoolCreatedEvent,
        'PUT': events.PoolUpdatedEvent,
        'GET': events.PoolLoadedEvent,
        'DELETE': events.PoolDeletedEvent,
    }


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=PoolFactory
)
class PoolWorkflowService(WorkflowAwareResource):
    """Pool workflow resource."""

    model = Pool


@resource(
    collection_path=PATH + '/versions',
    path=PATH + '/versions/{version_id}',
    cors_policy=CORS_POLICY,
    factory=PoolFactory
)
class PoolVersionsService(VersionsService):
    """Versioning of Pools."""

    model = Pool


@resource(
    path=PATH + '/history',
    cors_policy=CORS_POLICY,
    factory=PoolFactory
)
class PoolHistory(HistoryService):
    """Workflow history of Pools."""

    model = Pool
