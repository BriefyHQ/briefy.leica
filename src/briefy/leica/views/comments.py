"""Views to handle Comments creation."""
from briefy.ws.resources import RESTService
from briefy.leica.models import Comment
from briefy.ws import CORS_POLICY
from cornice.resource import resource


@resource(collection_path='/comments', path='/comments/{id}', cors_policy=CORS_POLICY)
class CommentService(RESTService):
    """Comments Service."""

    model = Comment
    friendly_name = model.__name__
    default_order_by = 'created_at'
