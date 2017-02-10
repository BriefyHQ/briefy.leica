"""Briefy Leica worker."""
from briefy.common.queue import IQueue
from briefy.common.queue.message import SQSMessage
from briefy.common.utils.data import Objectify
from briefy.common.worker.queue import QueueWorker
from briefy.leica.config import NEW_RELIC_LICENSE_KEY
from briefy.leica import logger
from briefy.leica.worker import actions
from zope.component import getUtility

import newrelic.agent


MESSAGE_DISPATCH = {
    'laure.assignment.validated': {
        'name': 'resolving validated assignment',
        'action': actions.validate_assignment,
        'success_notification': None,
        'failure_notification': None,
    },
    'laure.assignment.rejected': {
        'name': 'resolving invalidated assigment',
        'action': actions.invalidate_assignment,
        'success_notification': None,
        'failure_notification': None,
    },
    'laure.assignment.copied': {
        'name': 'resolving copied assets',
        'action': actions.approve_assignment,
        'success_notification': None,
        'failure_notification': None,
    },
    'laure.assignment.copy_failure': {
        'name': 'handling asset copy failure',
        'action': actions.asset_copy_malfunction,
        'success_notification': None,
        'failure_notification': None,
    }
}

"""
Dictionary for event dispatching. Expected format:
each key is the event name itself - each value being another dictionary
with the following keys:
 'name': String withthe action name for purposes of logging and creating other messages
 'action': A callable that will process the event 'objectified' payload,
           and return a tuple with a boolean and a dict the boolean indicates wether
           the action succeeded or failed; the dict is to be used
           as payload for the response event.
 'success_notification': briefy.BaseEvent subclass to be created when the action suceeds
 'failure_notification': briefy.BaseEvent subclass to be created when the action fails
"""


class Worker(QueueWorker):
    """Briefy.leica queue worker."""

    name = 'briefy.leica.worker'
    """Worker name."""

    input_queue = None
    """Queue to read event messages from."""

    run_interval = 1
    """Interval to fetch new messages from the queue."""

    _events_queue = None
    """Events queue."""

    @newrelic.agent.background_task(name='process_message', group='Task')
    def process_message(self, message: SQSMessage) -> bool:
        """Process a message retrieved from the input_queue.

        :param message: A message from the queue
        :returns: Status from the process
        """
        status = True

        body = message.body
        assignment = Objectify(body.get('data', {}))
        event = body.get('event_name', '')
        dispatch = Objectify(MESSAGE_DISPATCH.get(event, {}))

        if not dispatch:
            logger.info('Unknown event type - message {0} ignored'.format(body['id']))
            return True

        try:
            assignment_status, payload = dispatch.action(assignment)

        except Exception as error:
            status = False
            logger.error('Unknown exception raised on \'{0}\' assignment {1}. Error: {2}'.format(
                dispatch.name,
                assignment.dct,
                error))
            raise  # Let newrelic deal with it.
        event = None
        if status and dispatch.success_notification:
            event = dispatch.success_notification(payload)
        elif not status and dispatch.failure_notification:
            event = dispatch.failure_notification(payload)
        if event:
            event()
        return status


def main():
    """Initialize and execute the Worker."""
    queue = getUtility(IQueue, 'leica.queue')
    worker = Worker(logger_=logger, input_queue=queue)
    if NEW_RELIC_LICENSE_KEY:
        newrelic.agent.register_application(timeout=10.0)
    try:
        worker()
    except:
        logger.exception('{name} exiting due to an exception.'.format(name=Worker.name))
        raise