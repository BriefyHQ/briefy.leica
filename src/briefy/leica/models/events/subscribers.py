"""Model event subscribers for briefy.leica."""
from briefy.common.workflow.exceptions import WorkflowPermissionException
from briefy.leica import logger
from briefy.leica.models.events.asset import AssetCreatedEvent
from briefy.leica.models.events.asset import AssetUpdatedEvent
from briefy.leica.models.events.job import JobCreatedEvent
from pyramid.events import subscriber
from requests.exceptions import ConnectionError

import transaction


def safe_update_metadata(obj):
    """Execute asset update metadata method using transaction savepoint.

    :param obj: Asset model instance.
    """
    savepoint = transaction.savepoint()
    try:
        obj.update_metadata()
    except ConnectionError:
        savepoint.rollback()
        msg = 'Failure updating metadata for asset: {id} title: {title}.'
        logger.info(msg.format(id=obj.id, title=obj.title))


def safe_workflow_trigger_transitions(event, transitions, state='created'):
    """Helper to trigger each transition in order using an object event.

    :param event: briefy.ws request event.
    :param transitions: list of transitions names to be trrigered in order.
    :param state: the actual object state of the object to trigger the transitions.
    """
    obj = event.obj
    request = event.request
    if request is not None:
        user = request.user
        if user is not None:
            user = request.user
            wf = obj.workflow
            wf.context = user
            if wf.state.name == state:
                savepoint = transaction.savepoint()
                for transition_name in transitions:
                    try:
                        transition = getattr(wf, transition_name)
                        transition()
                    except AttributeError:
                        savepoint.rollback()
                        msg = 'Transition: {transition} not found in asset: {id} title: {title}.'
                        logger.info(msg.format(id=obj.id, title=obj.title,
                                               transition=transition_name))
                    except WorkflowPermissionException:
                        savepoint.rollback()
                        msg = 'Permission denied. Could not execute transition: {transition} for ' \
                              'asset: {id} state: {state}. user groups:{groups}'
                        logger.info(msg.format(id=obj.id, state=wf.state.name,
                                               transition=transition_name,
                                               groups=user.groups))


@subscriber(AssetCreatedEvent)
def asset_created_handler(event):
    """Handle asset created event."""
    safe_update_metadata(event.obj)
    transitions = ['submit', 'validate']
    safe_workflow_trigger_transitions(event, transitions=transitions)


@subscriber(JobCreatedEvent)
def job_created_handler(event):
    """Handle job created event."""
    transitions = ['submit']
    safe_workflow_trigger_transitions(event, transitions=transitions)


@subscriber(AssetUpdatedEvent)
def asset_updated_handler(event):
    """Handle asset updated event."""
    obj = event.obj
    safe_update_metadata(obj)