
"""Briefy Leica Queue."""
from briefy.common.queue import IQueue
from briefy.common.queue import Queue as BaseQueue
from briefy.common.utils.schema import Dictionary
from briefy.leica.config import LEICA_QUEUE
from zope.interface import implementer

import colander
import logging

logger = logging.getLogger('briefy.leica')


class Schema(colander.MappingSchema):
    """Payload for the mail queue."""

    data = colander.SchemaNode(Dictionary())


@implementer(IQueue)
class Queue(BaseQueue):
    """A Queue to handle messages to send emails."""

    name = LEICA_QUEUE
    _schema = Schema

    @property
    def payload(self):
        """Return an example payload for this queue.

        :returns: Dictionary representing the payload for this queue
        :rtype: dict
        """
        return {
            'data': {},
        }

LeicaQueue = Queue()
