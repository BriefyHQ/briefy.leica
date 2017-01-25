"""Views to handle Comments creation."""
from briefy.leica.events import comment as events
from briefy.leica.models import Comment
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


class CommentFactory(BaseFactory):
    """Comment context factory."""

    model = Comment

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:briefy', ['create', 'list', 'view']),
            (Allow, 'g:briefy_qa', ['create', 'list', 'view']),
            (Allow, 'g:professionals', ['create', 'list', 'view']),
            (Allow, 'g:customers', ['create', 'list', 'view']),
        ]
        return _acls


class CommentService(RESTService):
    """Comments Service."""

    model = Comment
    friendly_name = model.__name__
    default_order_by = 'created_at'
    default_order_direction = -1

    _default_notify_events = {
        'POST': events.CommentCreatedEvent,
        'PUT': events.CommentUpdatedEvent,
        'GET': events.CommentLoadedEvent,
        'DELETE': events.CommentDeletedEvent,
    }

    @property
    def filter_allowed_fields(self):
        """List of fields allowed in filtering and sorting."""
        allowed_fields = super().filter_allowed_fields
        # Remove assignment_id and asset_id
        allowed_fields.remove('entity_id')
        return allowed_fields

    def default_filters(self, query) -> object:
        """Default filters for this Service."""
        entity_id = self.request.matchdict.get('entity_id', '')
        query = query.filter(self.model.entity_id == entity_id)
        return query


ASSIGNMENT_PATH = '/assignments/{assignment_id}'

COLLECTION_PATH = '/assignments/{entity_id}/comments'
PATH = COLLECTION_PATH + '/{id}'


@resource(
    collection_path=COLLECTION_PATH,
    path=PATH,
    cors_policy=CORS_POLICY,
    factory=CommentFactory
)
class AssignmentCommentService(CommentService):
    """Comments for an Assignment."""


COLLECTION_PATH = ASSIGNMENT_PATH + '/assets/{entity_id}/comments'
PATH = COLLECTION_PATH + '/{id}'


@resource(
    collection_path=COLLECTION_PATH,
    path=PATH,
    cors_policy=CORS_POLICY,
    factory=CommentFactory
)
class AssetCommentService(CommentService):
    """Comments for an Asset."""


COLLECTION_PATH = ASSIGNMENT_PATH + '/orders/{entity_id}/comments'
PATH = COLLECTION_PATH + '/{id}'


@resource(
    collection_path=COLLECTION_PATH,
    path=PATH,
    cors_policy=CORS_POLICY,
    factory=CommentFactory
)
class OrderCommentService(CommentService):
    """Comments for an Order."""
