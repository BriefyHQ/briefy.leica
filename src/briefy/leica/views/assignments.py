"""Views to handle Assignments creation."""
from briefy.leica.events import assignment as events
from briefy.leica.models import Assignment
from briefy.ws import CORS_POLICY
from briefy.ws.resources import BaseResource
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from cornice.resource import view
from pyramid.httpexceptions import HTTPNotFound as NotFound
from pyramid.security import Allow

COLLECTION_PATH = '/assignments'
PATH = COLLECTION_PATH + '/{id}'


class AssignmentFactory(BaseFactory):
    """Assignment context factory."""

    model = Assignment

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:briefy_pm', ['create', 'delete', 'edit', 'list', 'view']),
            (Allow, 'g:briefy_qa', ['list', 'view']),
            (Allow, 'g:professionals', ['list'])
        ]
        return _acls


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=AssignmentFactory)
class AssignmentService(RESTService):
    """Assignment service."""

    model = Assignment
    friendly_name = model.__name__
    default_order_by = 'updated_at'
    filter_related_fields = [
        'project.title', 'title', 'professional.title', 'professional.main_email',
        'project.id', 'description', 'location.locality', 'location.country',
        'location.formatted_address', 'location.fullname', 'location.email',
        'professional_user', 'project_manager', 'scout_manager', 'qa_manager',
        'customer.title', 'pool.id', 'pool.title', 'pool.country'
    ]

    _default_notify_events = {
        'POST': events.AssignmentCreatedEvent,
        'PUT': events.AssignmentUpdatedEvent,
        'GET': events.AssignmentLoadedEvent,
        'DELETE': events.AssignmentDeletedEvent,
    }


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=AssignmentFactory
)
class AssignmentWorkflowService(WorkflowAwareResource):
    """Assignment workflow resource."""

    model = Assignment
    friendly_name = Assignment.__name__


@resource(
    collection_path=PATH + '/versions',
    path=PATH + '/versions/{version_id}',
    cors_policy=CORS_POLICY,
    factory=AssignmentFactory
)
class AssignmentVersionsService(BaseResource):
    """Versioning of Assignments."""

    model = Assignment
    friendly_name = Assignment.__name__
    default_order_by = 'title'

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
