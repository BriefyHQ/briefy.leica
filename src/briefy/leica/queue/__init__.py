"""Briefy Leica Queue."""
from briefy.common.queue import IQueue
from briefy.common.queue import Queue as BaseQueue
from briefy.leica.config import LEICA_QUEUE
from zope.interface import implementer

import colander
import logging

logger = logging.getLogger('briefy.leica')


class Schema(colander.MappingSchema):
    """Payload for the leica queue."""

    pass


@implementer(IQueue)
class Queue(BaseQueue):
    """A Queue to handle messages to send emails."""

    name = LEICA_QUEUE
    """Queue name."""

    _schema = Schema
    """Validation schema."""

    @property
    def payload(self) -> dict:
        """Return an example payload for this queue.

        :returns: Dictionary representing the payload for this queue
        """
        return {
            # TBD
        }


LeicaQueue = Queue()
