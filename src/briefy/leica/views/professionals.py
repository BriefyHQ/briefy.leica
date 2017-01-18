"""Views to handle Professionals creation."""
from briefy.leica.events import professional as events
from briefy.leica.models import Professional
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow

COLLECTION_PATH = '/professionals'
PATH = COLLECTION_PATH + '/{id}'


class ProfessionalFactory(BaseFactory):
    """Professional context factory."""

    model = Professional

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:briefy_scout', ['add', 'delete', 'edit', 'list', 'view']),
            (Allow, 'g:briefy_finance', ['add', 'delete', 'edit', 'list', 'view']),
            (Allow, 'g:briefy_qa', ['list', 'view']),
        ]
        return _acls


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=ProfessionalFactory)
class ProfessionalService(RESTService):
    """Professionals Service."""

    model = Professional
    friendly_name = model.__name__
    default_order_by = 'title'
    filter_related_fields = [
        'title', 'customer_user', 'project_manager', 'customer.title',
        'main_location.formatted_address', 'main_location.country',
        'main_location.locality', 'pools.id', 'pools.title', 'pools.country'
    ]

    _default_notify_events = {
        'POST': events.ProfessionalCreatedEvent,
        'PUT': events.ProfessionalUpdatedEvent,
        'GET': events.ProfessionalLoadedEvent,
        'DELETE': events.ProfessionalDeletedEvent,
    }


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=ProfessionalFactory
)
class ProfessionalWorkflowService(WorkflowAwareResource):
    """Professional workflow resource."""

    model = Professional
    friendly_name = Professional.__name__
