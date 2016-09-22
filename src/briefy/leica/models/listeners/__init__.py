"""Sqlalchemy event listeners for briefy.leica models."""
from briefy.common.workflow.exceptions import WorkflowPermissionException
from briefy.leica import models
from briefy.leica import logger
from requests.exceptions import ConnectionError
from sqlalchemy import event

import transaction


@event.listens_for(models.Asset, 'after_insert')
def auto_workflow_asset_insert(mapper, connection, target):
    """Handler called when instance is flushed.

    :param target: Asset model instance.
    :param flush_context: sqlalchemy flush context.
    :param attrs:
    :return:
    """
    request = getattr(target, 'request', None)
    if request is not None:
        target.request = request
        user = request.user
        if user is not None:
            user = request.user
            wf = target.workflow
            wf.context = user
            if wf.state.name == 'created':
                savepoint = transaction.savepoint()
                try:
                    wf.submit()
                    wf.validate()
                except WorkflowPermissionException:
                    savepoint.rollback()
                    msg = 'Failure in automatic transition for asset: {id} title: {title}.'
                    logger.info(msg.format(id=target.id, title=target.title))


@event.listens_for(models.Asset, 'refresh_flush')
def update_metadata_asset_refresh_flush(target, flush_context, attrs):
    """Handler called when instance is flushed.

    :param target: Asset model instance.
    :param flush_context: sqlalchemy flush context.
    :param attrs:
    :return:
    """
    savepoint = transaction.savepoint()
    try:
        target.update_metadata()
    except ConnectionError:
        savepoint.rollback()
        msg = 'Failure updating metadata for asset: {id} title: {title}.'
        logger.info(msg.format(id=target.id, title=target.title))
