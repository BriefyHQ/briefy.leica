"""Views to handle Comments creation."""
from briefy.ws.resources import RESTService
from briefy.leica.models import Comment
from briefy.ws import CORS_POLICY
from cornice.resource import resource


class CommentsService(RESTService):
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


JOB_PATH = '/jobs/{job_id}'

COLLECTION_PATH = '/jobs/{entity_id}/comments'
PATH = COLLECTION_PATH + '/{id}'


@resource(
    collection_path=COLLECTION_PATH,
    path=PATH,
    cors_policy=CORS_POLICY
)
class JobCommentService(CommentsService):
    """Comments for a Job."""


COLLECTION_PATH = JOB_PATH + '/assets/{entity_id}/comments'
PATH = COLLECTION_PATH + '/{id}'


@resource(
    collection_path=COLLECTION_PATH,
    path=PATH,
    cors_policy=CORS_POLICY
)
class AssetCommentService(CommentsService):
    """Comments for an asset."""
