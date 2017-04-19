"""Custom briefy.leica events and subscribers."""
from briefy.common.event import TaskEvent
from briefy.leica import logger


class LeicaTaskEvent(TaskEvent):
    """A task on Leica."""

    logger = logger
