"""Model event subscribers for briefy.leica."""
from briefy.common.workflow.exceptions import WorkflowPermissionException
from briefy.leica import logger
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
    user = getattr(event, 'user', None)
    if request is None and user is None:
        return None
    user = user if user else request.user
    if user is None:
        return None

    wf = obj.workflow
    wf.context = user
    if wf.state.name != state:
        return None
    savepoint = transaction.savepoint()
    for transition_name, message in transitions:
        try:
            transition = getattr(wf, transition_name)
            transition(message=message)
        except AttributeError as error:
            savepoint.rollback()
            msg = 'Transition: {transition} not found in asset: {id} title: {title}. ' \
                  'Error: {error}'
            logger.error(
                msg.format(
                    id=obj.id,
                    title=obj.title,
                    transition=transition_name,
                    error=error
                )
            )
        except WorkflowPermissionException as error:
            savepoint.rollback()
            msg = 'Permission denied. Could not execute transition: {transition} for ' \
                  'asset: {id} state: {state}. user groups:{groups} Error: {error}'
            logger.error(
                msg.format(
                    id=obj.id,
                    state=wf.state.name,
                    transition=transition_name,
                    groups=user.groups,
                    error=error
                )
            )
    return None
