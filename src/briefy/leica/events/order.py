"""Custom briefy.leica events for model Order."""
from briefy.leica import logger
from briefy.ws.resources import events


class OrderCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify Order creation."""

    event_name = 'order.created'
    logger = logger


class OrderUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify job Order update."""

    event_name = 'order.updated'
    logger = logger


class OrderDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify Order delete."""


class OrderLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify Order load."""
