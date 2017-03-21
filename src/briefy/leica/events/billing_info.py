"""Custom briefy.leica events for model ProfessionalBillingInfo."""
from briefy.leica import logger
from briefy.ws.resources import events


class CustomerBillingInfoCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify CustomerBillingInfo creation."""

    event_name = 'customerbillinginfo.created'
    logger = logger


class CustomerBillingInfoUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify customerBillingInfo update."""

    event_name = 'customerbillinginfo.updated'
    logger = logger


class CustomerBillingInfoDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify customerBillingInfo delete."""


class CustomerBillingInfoLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify customerBillingInfo load."""


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
