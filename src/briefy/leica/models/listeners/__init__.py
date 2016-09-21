"""Sqlalchemy event listeners for briefy.leica models."""
from briefy.common.workflow.exceptions import WorkflowPermissionException
from briefy.leica import models
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
    user = target.request.user
    workflow = target.workflow
    workflow.context = user
    if workflow.state.name == 'created':
        try:
            # automatic transition after created
            workflow.submit()
        except WorkflowPermissionException:
            # TODO: logging
            pass
    try:
        target.update_metadata()
    except ConnectionError:
        # TODO: logging
        pass
