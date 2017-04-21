"""Comment Workflow."""
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import BriefyWorkflow

import logging


logger = logging.getLogger(__name__)


class CommentWorkflow(BriefyWorkflow):
    """Workflow for a Comment."""

    entity = 'comment'
    initial_state = 'created'

    created = WS(
        'created', 'Created',
        'Comment created.'
    )
