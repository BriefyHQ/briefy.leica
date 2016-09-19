"""Views to handle Comments creation."""
from briefy.ws.resources import RESTService
from briefy.ws.resources import WorkflowAwareResource
from briefy.leica.models import Comment
from briefy.ws import CORS_POLICY
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
            (Allow, 'g:briefy_pm', ['add', 'delete', 'edit', 'list', 'view'])
        ]
        return _acls


class CommentService(RESTService):
    """Comments Service."""

    model = Comment
    friendly_name = model.__name__
    default_order_by = 'created_at'

    @property
    def filter_allowed_fields(self):
        """List of fields allowed in filtering and sorting."""
        allowed_fields = super().filter_allowed_fields
        # Remove job_id and asset_id
        allowed_fields.remove('entity_id')
        return allowed_fields

    @property
    def default_filters(self) -> tuple:
        """Default filters for this Service."""
        entity_id = self.request.matchdict.get('entity_id', '')
        filters = list(super().default_filters)
        filters.append((self.model.entity_id == entity_id))
        return tuple(filters)


class CommentsWorkflowService(WorkflowAwareResource):
    """Comments workflow service."""
    model = Comment
    friendly_name = Comment.__name__


JOB_PATH = '/jobs/{job_id}'

COLLECTION_PATH = '/jobs/{entity_id}/comments'
PATH = COLLECTION_PATH + '/{id}'


@resource(
    collection_path=COLLECTION_PATH,
    path=PATH,
    cors_policy=CORS_POLICY,
    factory=CommentFactory
)
class JobCommentService(CommentService):
    """Comments for a Job."""


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY
)
class JobCommentWorkflowService(CommentsWorkflowService):
    """JobComment workflow resource."""


COLLECTION_PATH = JOB_PATH + '/assets/{entity_id}/comments'
PATH = COLLECTION_PATH + '/{id}'


@resource(
    collection_path=COLLECTION_PATH,
    path=PATH,
    cors_policy=CORS_POLICY,
    factory=CommentFactory
)
class AssetCommentService(CommentService):
    """Comments for an asset."""


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY
)
class AssetCommentWorkflowService(CommentsWorkflowService):
    """AssetComment workflow resource."""
