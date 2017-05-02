"""Event subscribers for briefy.leica.models.comment.Comment."""
from briefy.leica.cache import cache_manager
from briefy.leica.events import comment as events
from pyramid.events import subscriber


@subscriber(events.CommentCreatedEvent)
def comment_created_handler(event):
    """Handle Comment created event."""
    comment = event.obj
    cache_manager.refresh(comment)
    if comment.entity:
        cache_manager.refresh(comment.entity)
