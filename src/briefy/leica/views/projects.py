"""Views to handle Projects creation."""
from briefy.leica.models import Project
from briefy.leica.models.events import project as events
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws import CORS_POLICY
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow

COLLECTION_PATH = '/projects'
PATH = COLLECTION_PATH + '/{id}'


class ProjectFactory(BaseFactory):
    """Project context factory."""

    model = Project

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.
        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:briefy_pm', ['add', 'delete', 'edit', 'list', 'view']),
            (Allow, 'g:briefy_qa', ['list', 'view'])
        ]
        return _acls


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=ProjectFactory)
class ProjectService(RESTService):
    """Projects Service."""

    model = Project
    friendly_name = model.__name__
    default_order_by = 'created_at'

    _default_notify_events = {
        'POST': events.ProjectCreatedEvent,
        'PUT': events.ProjectUpdatedEvent,
        'GET': events.ProjectLoadedEvent,
        'DELETE': events.ProjectDeletedEvent,
    }


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=ProjectFactory
)
class ProjectWorkflow(WorkflowAwareResource):
    """Project workflow resource."""

    model = Project
    friendly_name = Project.__name__
