"""Custom briefy.leica events for model Assignment."""
from briefy.leica import logger
from briefy.ws.resources import events


class AssignmentCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify Assignment creation."""

    event_name = 'assignment.created'
    logger = logger


class AssignmentUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify Assignment update."""

    event_name = 'assignment.updated'
    logger = logger


class AssignmentDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify Assignment delete."""


class AssignmentLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify Assignment load."""
