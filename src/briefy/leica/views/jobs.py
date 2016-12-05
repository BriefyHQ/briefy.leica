"""Views to handle Jobs creation."""
from briefy.leica.models import Job
from briefy.leica.models.events import job as events
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws import CORS_POLICY
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


COLLECTION_PATH = '/jobs'
PATH = COLLECTION_PATH + '/{id}'


class JobFactory(BaseFactory):
    """Job context factory."""

    model = Job

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.
        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:briefy_pm', ['add', 'delete', 'edit', 'list', 'view'])
        ]
        return _acls


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=JobFactory)
class JobService(RESTService):
    """Jobs service."""

    model = Job
    friendly_name = model.__name__
    default_order_by = 'created_at'
    filter_related_fields = ['project.title']

    _default_notify_events = {
        'POST': events.JobCreatedEvent,
        'PUT': events.JobUpdatedEvent,
        'GET': events.JobLoadedEvent,
        'DELETE': events.JobDeletedEvent,
    }


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=JobFactory
)
class JobWorkflow(WorkflowAwareResource):
    """Job workflow resource."""

    model = Job
    friendly_name = Job.__name__
