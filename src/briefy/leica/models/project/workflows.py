"""Project Workflow."""
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState as WS

import logging


logger = logging.getLogger(__name__)


class ProjectWorkflow(BriefyWorkflow):
    """Workflow for a Project."""

    entity = 'project'
    initial_state = 'created'

    created = WS(
        'created', 'Created',
        'Project created.'
    )
