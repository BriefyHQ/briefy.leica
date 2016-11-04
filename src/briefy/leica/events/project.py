"""Custom briefy.leica events for model Project."""
from briefy.leica import logger
from briefy.ws.resources import events


class ProjectCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify project creation."""

    event_name = 'project.created'
    logger = logger


class ProjectUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify project update."""

    event_name = 'project.updated'
    logger = logger


class ProjectDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify project delete."""


class ProjectLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify project load."""
