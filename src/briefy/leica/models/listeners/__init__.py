"""Sqlalchemy event listeners for briefy.leica models."""
from briefy.common.workflow.exceptions import WorkflowPermissionException
from briefy.leica import models
from briefy.leica import logger
from copy import copy
from requests.exceptions import ConnectionError
from sqlalchemy import event


@event.listens_for(models.Asset, 'refresh_flush')
def receive_asset_refresh_flush(target, flush_context, attrs):
    """Handler called when instance is flushed.

    :param target: Asset model instance.
    :param flush_context: sqlalchemy flush context.
    :param attrs:
    :return:
    """
    request = (getattr(target, 'request', None))
    if request is not None:
        user = request.user
        if user is not None:
            user = request.user
            workflow = target.workflow
            workflow.context = user
            if workflow.state.name == 'created':
                try:
                    workflow.submit()
                    # TODO: create system user singleton and use hre
                    system_user = copy(user)
                    system_user.groups.append('g:system')
                    workflow.context = user
                    workflow.validate()
                except WorkflowPermissionException:
                    msg = 'Failure in automatic transition for asset: {id} title: {title}.'
                    logger.debug(msg.format(id=target.id, title=target.title))
    try:
        target.update_metadata()
    except ConnectionError:
        msg = 'Failure updating metadata for asset: {id} title: {title}.'
        logger.debug(msg.format(id=target.id, title=target.title))
