"""Comment Workflow."""
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState as WS

import logging


logger = logging.getLogger(__name__)


class CommentWorkflow(BriefyWorkflow):
    """Workflow for a Comment."""

    entity = 'comments'
    initial_state = 'created'

    created = WS(
        'created', 'Created',
        'Comment created.'
    )
