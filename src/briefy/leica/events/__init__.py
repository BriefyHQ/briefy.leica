"""Custom briefy.leica events and subscribers."""
from briefy.common.event import BaseEvent
from briefy.common.event import IDataEvent
from briefy.leica import logger


class ILeicaEvent(IDataEvent):
    """Interface for IDataEvent on a Leica object."""


# class ILeicaSent(IMailEvent):
#     """A Leica was sent."""


class LeicaEvent(BaseEvent):
    """A event to a Leica."""

    logger = logger


# @implementer(ILeicaSent)
# class LeicaSent(LeicaEvent):
#     """A Leica was sent."""

#     event_name = 'leica.sent'
