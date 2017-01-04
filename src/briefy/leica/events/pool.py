"""Custom briefy.leica events for model Pool."""
from briefy.leica import logger
from briefy.ws.resources import events


class PoolCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify Pool creation."""

    event_name = 'pool.created'
    logger = logger


class PoolUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify Pool update."""

    event_name = 'pool.updated'
    logger = logger


class PoolDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify Pool delete."""


class PoolLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify Pool load."""
