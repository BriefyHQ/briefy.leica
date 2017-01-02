"""Custom briefy.leica events for model JobPool."""
from briefy.leica import logger
from briefy.ws.resources import events


class JobPoolCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify job pool creation."""

    event_name = 'jobpool.created'
    logger = logger


class JobPoolUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify job pool update."""

    event_name = 'jobpool.updated'
    logger = logger


class JobPoolDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify job order delete."""


class JobPoolLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify job pool load."""
