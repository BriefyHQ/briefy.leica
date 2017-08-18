"""Views to handle Professionals creation."""
from briefy.leica.events import professional as events
from briefy.leica.models import Photographer
from briefy.leica.models import Professional
from briefy.leica.views import email_in_use
from briefy.leica.views import EMAIL_IN_USE_MESSAGE
from briefy.ws import CORS_POLICY
from briefy.ws.resources import HistoryService
from briefy.ws.resources import RESTService
from briefy.ws.resources import VersionsService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from cornice.resource import view
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
    default_order_by = 'title'
    filter_related_fields = [
        'title', '_main_location.formatted_address', '_main_location.country',
        '_main_location.locality', 'pools.id', 'pools.title', 'pools.country'
    ]

    _validators = (
        ('GET', ('validate_id', )),
        ('PUT', ('validate_id', )),
        ('POST', ('email_in_use', ))
    )

    _default_notify_events = {
        'POST': events.ProfessionalCreatedEvent,
        'PUT': events.ProfessionalUpdatedEvent,
        'GET': events.ProfessionalLoadedEvent,
        'DELETE': events.ProfessionalDeletedEvent,
    }

    def email_in_use(self, request):
        """Email validation."""
        if not email_in_use(request):
            self.raise_invalid(name='email', description=EMAIL_IN_USE_MESSAGE)

    @view(validators='_run_validators', permission='create')
    def collection_post(self, model=None):
        """Add a new instance of a Professional.

        For now all Professionals are Photographers, but this needs to change
        :returns: Newly created instance of model Photographer.
        """
        model = Photographer
        return super().collection_post(model=model)


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=ProfessionalFactory
)
class ProfessionalWorkflowService(WorkflowAwareResource):
    """Professional workflow resource."""

    model = Professional


@resource(
    collection_path=PATH + '/versions',
    path=PATH + '/versions/{version_id}',
    cors_policy=CORS_POLICY,
    factory=ProfessionalFactory
)
class ProfessionalVersionsService(VersionsService):
    """Versioning of Professionals."""

    model = Professional


@resource(
    collection_path=PATH + '/history',
    path=PATH + '/history/{item_id}',
    cors_policy=CORS_POLICY,
    factory=ProfessionalFactory
)
class ProfessionalHistory(HistoryService):
    """Workflow history of Professionals."""

    model = Professional
