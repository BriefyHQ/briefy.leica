"""Custom briefy.leica events for model Job."""
from briefy.leica import logger
from briefy.ws.resources import events


class JobCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify job creation."""

    event_name = 'jobassignment.created'
    logger = logger


class JobUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify job update."""

    event_name = 'jobassignment.updated'
    logger = logger


class JobDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify job delete."""


class JobLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify job load."""
