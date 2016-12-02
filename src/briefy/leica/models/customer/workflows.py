"""Customer Workflow."""
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState as WS

import logging


logger = logging.getLogger(__name__)


class CustomerWorkflow(BriefyWorkflow):
    """Workflow for a Customer."""

    entity = 'customers'
    initial_state = 'created'

    created = WS('created', 'Created')
    """Customer created."""
