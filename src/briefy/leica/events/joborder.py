"""Custom briefy.leica events for model JobOrder."""
from briefy.leica import logger
from briefy.ws.resources import events


class JobOrderCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify job order creation."""

    event_name = 'joborder.created'
    logger = logger


class JobOrderUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify job order update."""

    event_name = 'joborder.updated'
    logger = logger


class JobOrderDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify job order delete."""


class JobOrderLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify job order load."""
