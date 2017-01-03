"""Views to handle JobPools creation."""
from briefy.leica.events import jobpool as events
from briefy.leica.models import JobPool
from briefy.ws import CORS_POLICY
from briefy.ws.resources import BaseResource
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from cornice.resource import view
from pyramid.httpexceptions import HTTPNotFound as NotFound
from pyramid.security import Allow

COLLECTION_PATH = '/pools'
PATH = COLLECTION_PATH + '/{id}'


class JobPoolFactory(BaseFactory):
    """Job pool context factory."""

    model = JobPool

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
          factory=JobPoolFactory)
class JobPoolService(RESTService):
    """Job Pool service."""

    model = JobPool
    friendly_name = model.__name__
    default_order_by = 'title'
    filter_related_fields = []

    _default_notify_events = {
        'POST': events.JobPoolCreatedEvent,
        'PUT': events.JobPoolUpdatedEvent,
        'GET': events.JobPoolLoadedEvent,
        'DELETE': events.JobPoolDeletedEvent,
    }


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=JobPoolFactory
)
class JobPoolWorkflow(WorkflowAwareResource):
    """Job pool workflow resource."""

    model = JobPool
    friendly_name = model.__name__


@resource(
    collection_path=PATH + '/versions',
    path=PATH + '/versions/{version_id}',
    cors_policy=CORS_POLICY,
    factory=JobPoolFactory
)
class JobPoolVersions(BaseResource):
    """Versioning of Job pools."""

    model = JobPool
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
