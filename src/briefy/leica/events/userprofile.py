"""Custom briefy.leica events for model UserProfile."""
from briefy.leica import logger
from briefy.ws.resources import events


class UserProfileCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify UserProfile creation."""

    event_name = 'userprofile.created'
    logger = logger


class UserProfileUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify UserProfile update."""

    event_name = 'userprofile.updated'
    logger = logger


class UserProfileDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify UserProfile delete."""


class UserProfileLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify UserProfile load."""
