
"""Briefy Leica worker."""
from briefy.common.queue import IQueue
from briefy.common.worker.queue import QueueWorker
from briefy.leica.config import NEW_RELIC_LICENSE_KEY
# from briefy.leica.events import LeicaSent
# from briefy.leica.providers import ILeica
from zope.component import getUtility

import logging
import newrelic.agent

logger = logging.getLogger('briefy.leica')


class Worker(QueueWorker):
    """Leica queue worker."""

    name = 'leica.worker'
    input_queue = None
    run_interval = None
    _events_queue = None
    _provider = None

    @property
    def provider(self):
        """Leica gateway provider to handle messages."""
        pass

    def notify(self, leica_message):
        """Notify a LeicaSent event.

        :param leica_message: Leica message to be used for the event
        :type leica_message: LeicaMessage
        """
        # event = LeicaSent(leica_message)
        # event()
        pass

    def prepare_leica_message(self, leica_message, body):
        """Update LeicaMessage with SQSMessage fields.

        :param leica_message: Leica message to be used for the event
        :type leica_message: LeicaMessage
        :param body: Body of a briefy.common.queue.message.SQSMessage
        :type body: dict
        :returns: Leica message to be used for the event
        :rtype: LeicaMessage
        """
        leica_message.entity = body.get('entity')
        leica_message.guid = body.get('guid')
        leica_message.event_name = body.get('event_name')
        return leica_message

    @newrelic.agent.background_task(name='process_message', group='Task')
    def process_message(self, message):
        """Process a message retrieved from the input_queue.

        :param message: A message from the queue
        :type message: boto3.resources.factory.sqs.Message
        :returns: Status from the process
        :rtype: bool
        """
        status = True
        body = message.body
        params = {
            'data': body.get('data', {}),
        }
        leica_message = self.provider.send_template(**params)
        leica_message = self.prepare_leica_message(leica_message, body)
        self.notify(leica_message)
        return status


def main():
    """Initialize and execute the Worker."""
    queue = getUtility(IQueue, 'leica.queue')
    worker = Worker(input_queue=queue)
    if NEW_RELIC_LICENSE_KEY:
        newrelic.agent.register_application(timeout=10.0)
    try:
        worker()
    except:
        logger.exception(
            '{} exiting due to an exception.'.format(Worker.name)
        )
