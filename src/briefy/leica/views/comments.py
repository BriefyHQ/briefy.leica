"""Views to handle Comments creation."""
from briefy.leica.events import comment as events
from briefy.leica.models import Comment
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow
from pyramid.security import Deny
from sqlalchemy.orm.query import Query

import typing as t


class CommentFactory(BaseFactory):
    """Comment context factory."""

    model = Comment

    __base_acl__ = [
        (Allow, 'g:briefy', ['create', 'list', 'view']),
        (Allow, 'g:professionals', ['create', 'list', 'view']),
        (Allow, 'g:customers', ['create', 'list', 'view']),
    ]


class CommentService(RESTService):
    """Comments Service."""

    model = Comment
    default_order_by = 'created_at'
    default_order_direction = -1

    _default_notify_events = {
        'POST': events.CommentCreatedEvent,
        'PUT': events.CommentUpdatedEvent,
        'GET': events.CommentLoadedEvent,
        'DELETE': events.CommentDeletedEvent,
    }

    @property
    def filter_allowed_fields(self) -> t.Sequence[str]:
        """List of fields allowed in filtering and sorting."""
        allowed_fields = list(super().filter_allowed_fields)
        # Remove assignment_id and asset_id
        allowed_fields.remove('entity_id')
        return allowed_fields

    def default_filters(self, query: Query) -> Query:
        """Apply default filters for Comments resource..

        :param query: Base query.
        :return: Query with additional filters appliet to it.
        """
        request = self.request
        entity_id = request.matchdict.get('entity_id', '')
        user = request.user
        groups = user.groups
        query = query.filter(self.model.entity_id == entity_id)
        # External users should not access internal notes
        if 'g:briefy' not in groups:
            query = query.filter(self.model.internal.is_(False))
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


COLLECTION_PATH = '/orders/{entity_id}/comments'
PATH = COLLECTION_PATH + '/{id}'


@resource(
    collection_path=COLLECTION_PATH,
    path=PATH,
    cors_policy=CORS_POLICY,
    factory=CommentFactory
)
class OrderCommentService(CommentService):
    """Comments for an Order."""


COLLECTION_PATH = '/professionals/{entity_id}/comments'
PATH = COLLECTION_PATH + '/{id}'


class ProfessionalsCommentFactory(BaseFactory):
    """Comment context factory."""

    model = Comment

    __base_acl__ = [
        (Allow, 'g:briefy', ['create', 'list', 'view']),
        (Deny, 'g:professionals', ['create', 'list', 'view']),
        (Deny, 'g:customers', ['create', 'list', 'view']),
    ]


@resource(
    collection_path=COLLECTION_PATH,
    path=PATH,
    cors_policy=CORS_POLICY,
    factory=ProfessionalsCommentFactory
)
class ProfessionalCommentService(CommentService):
    """Comments for a Professional."""
