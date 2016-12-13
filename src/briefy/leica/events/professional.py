"""Custom briefy.leica events for model Professional."""
from briefy.leica import logger
from briefy.ws.resources import events


class ProfessionalCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify professional creation."""

    event_name = 'professional.created'
    logger = logger


class ProfessionalUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify professional update."""

    event_name = 'professional.updated'
    logger = logger


class ProfessionalDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify professional delete."""


class ProfessionalLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify professional load."""
