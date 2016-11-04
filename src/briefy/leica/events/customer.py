"""Custom briefy.leica events for model Customer."""
from briefy.leica import logger
from briefy.ws.resources import events


class CustomerCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify customer creation."""

    event_name = 'customer.created'
    logger = logger


class CustomerUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify customer update."""

    event_name = 'customer.updated'
    logger = logger


class CustomerDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify customer delete."""


class CustomerLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify customer load."""
