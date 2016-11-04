"""Custom briefy.leica events for model Comment and InternalComment."""
from briefy.leica import logger
from briefy.ws.resources import events


class CommentCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify comment creation."""

    event_name = 'comment.created'
    logger = logger


class CommentUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify comment update."""

    event_name = 'comment.updated'
    logger = logger


class CommentDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify comment delete."""


class CommentLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify comment load."""
