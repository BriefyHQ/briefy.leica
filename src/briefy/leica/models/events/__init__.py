"""Custom briefy.leica events and subscribers"""
from briefy.common.workflow.exceptions import WorkflowPermissionException
from briefy.leica import logger
from briefy.ws.resources import events
from pyramid.events import subscriber
from requests.exceptions import ConnectionError

import transaction


class AssetCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify asset creation."""


class AssetUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify asset update."""


class AssetDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify asset delete."""


class AssetLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify asset load."""


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


@subscriber(AssetCreatedEvent)
def asset_created_handler(event):
    """Handle asset created event."""
    obj = event.obj
    request = event.request

    safe_update_metadata(obj)

    if request is not None:
        user = request.user
        if user is not None:
            user = request.user
            wf = obj.workflow
            wf.context = user
            if wf.state.name == 'created':
                savepoint = transaction.savepoint()
                try:
                    wf.submit()
                    wf.validate()
                except WorkflowPermissionException:
                    savepoint.rollback()
                    msg = 'Failure in automatic transition for asset: {id} title: {title}.'
                    logger.info(msg.format(id=obj.id, title=obj.title))


@subscriber(AssetUpdatedEvent)
def asset_updated_handler(event):
    """Handle asset updated event."""
    obj = event.obj
    safe_update_metadata(obj)
