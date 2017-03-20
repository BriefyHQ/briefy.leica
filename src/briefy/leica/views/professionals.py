"""Views to handle Professionals creation."""
from briefy.leica.events import billing_info as billing_events
from briefy.leica.events import professional as events
from briefy.leica.models import Professional
from briefy.leica.models import ProfessionalBillingInfo
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
        'title', '_main_location.formatted_address', '_main_location.country',
        '_main_location.locality', 'pools.id', 'pools.title', 'pools.country'
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


class ProfessionalBillingInfoFactory(BaseFactory):
    """ProfessionalBillingInfo context factory."""

    model = ProfessionalBillingInfo

    __base_acl__ = [
        (Allow, 'g:professionals', ['create', 'list', 'view', 'edit']),
        (Allow, 'g:briefy_scout', ['create', 'list', 'view', 'edit']),
        (Allow, 'g:briefy_finance', ['create', 'list', 'view', 'edit']),
    ]


COLLECTION_PATH = '/professionals/{professional_id}/billing'
PATH = COLLECTION_PATH + '/{id}'


@resource(
    collection_path=COLLECTION_PATH,
    path=PATH,
    cors_policy=CORS_POLICY,
    factory=ProfessionalBillingInfoFactory
)
class ProfessionalBillingInfoService(RESTService):
    """ProfessionalBillingInfo Service."""

    model = ProfessionalBillingInfo
    friendly_name = model.__name__
    default_order_by = 'created_at'
    default_order_direction = -1

    _default_notify_events = {
        'POST': billing_events.ProfessionalBillingInfoCreatedEvent,
        'PUT': billing_events.ProfessionalBillingInfoUpdatedEvent,
        'GET': billing_events.ProfessionalBillingInfoLoadedEvent,
        'DELETE': billing_events.ProfessionalBillingInfoDeletedEvent,
    }

    @property
    def filter_allowed_fields(self):
        """List of fields allowed in filtering and sorting."""
        allowed_fields = super().filter_allowed_fields
        # Remove professional_id
        allowed_fields.remove('professional_id')
        return allowed_fields

    def default_filters(self, query) -> object:
        """Default filters for this Service."""
        professional_id = self.request.matchdict.get('professional_id', '')
        query = query.filter(self.model.professional_id == professional_id)
        return query
