"""Views to handle Assignments creation."""
from briefy.leica.events import assignment as events
from briefy.leica.models import Assignment
from briefy.leica.models import Professional
from briefy.ws import CORS_POLICY
from briefy.ws.resources import HistoryService
from briefy.ws.resources import RESTService
from briefy.ws.resources import VersionsService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
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
            (Allow, 'g:professionals', ['list', 'view', 'edit']),
        ]
        return _acls


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=AssignmentFactory)
class AssignmentService(RESTService):
    """Assignment service."""

    model = Assignment
    default_order_by = 'updated_at'
    filter_related_fields = [
        'project.title', 'title', 'professional.title', 'professional.email',
        'project.id', 'description', 'location.locality', 'location.country',
        'location.formatted_address', 'location.fullname', 'location.email',
        'professional_user', 'project_manager', 'scout_manager', 'qa_manager',
        'customer.title', 'pool.id', 'pool.title', 'pool.country', 'availability',
        'last_approval_date', 'submission_date',
    ]

    _default_notify_events = {
        'POST': events.AssignmentCreatedEvent,
        'PUT': events.AssignmentUpdatedEvent,
        'GET': events.AssignmentLoadedEvent,
        'DELETE': events.AssignmentDeletedEvent,
    }

    def default_filters(self, query) -> object:
        """Default filters to be applied to every query.

        This is supposed to be specialized by resource classes.
        :returns: A tuple of default filters to be applied to queries.
        """
        user = self.request.user
        custom_filter = self.request.params.get('_custom_filter')
        if 'g:professionals' in user.groups and custom_filter == 'pool':
            # disable security for this custom filter
            self.enable_security = False
            professional = Professional.get(user.id)
            pool_ids = [item.id for item in professional.pools]
            query = query.filter(
                Assignment.pool_id.in_(pool_ids),
                Assignment.state == 'published'
            )
        return query


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=AssignmentFactory
)
class AssignmentWorkflowService(WorkflowAwareResource):
    """Assignment workflow resource."""

    model = Assignment
    enable_security = False


@resource(
    collection_path=PATH + '/versions',
    path=PATH + '/versions/{version_id}',
    cors_policy=CORS_POLICY,
    factory=AssignmentFactory
)
class AssignmentVersionsService(VersionsService):
    """Versioning of Assignments."""

    model = Assignment
    default_order_by = 'title'


@resource(
    collection_path=PATH + '/history',
    path=PATH + '/history/{item_id}',
    cors_policy=CORS_POLICY,
    factory=AssignmentFactory
)
class AssignmentHistory(HistoryService):
    """Workflow history of assignments."""

    model = Assignment
