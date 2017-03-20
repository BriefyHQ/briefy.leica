"""Custom briefy.leica events for model ProfessionalBillingInfo."""
from briefy.leica import logger
from briefy.ws.resources import events


class ProfessionalBillingInfoCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify ProfessionalBillingInfo creation."""

    event_name = 'professionalbillinginfo.created'
    logger = logger


class ProfessionalBillingInfoUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify professionalBillingInfo update."""

    event_name = 'professionalbillinginfo.updated'
    logger = logger


class ProfessionalBillingInfoDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify professionalBillingInfo delete."""


class ProfessionalBillingInfoLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify professionalBillingInfo load."""
