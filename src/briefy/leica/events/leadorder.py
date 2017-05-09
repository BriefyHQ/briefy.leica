"""Custom briefy.leica events for model Lead."""
from briefy.leica import logger
from briefy.ws.resources import events


class LeadOrderCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify Lead order creation."""

    event_name = 'leadorder.created'
    logger = logger


class LeadOrderUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify a Lead order update."""

    event_name = 'leadorder.updated'
    logger = logger


class LeadOrderDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify a Lead order delete."""


class LeadOrderLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify a Lead order load."""
