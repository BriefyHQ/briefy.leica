"""Professional workflow."""
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState


import logging


logger = logging.getLogger(__name__)


class ProfessionalWorkflow(BriefyWorkflow):
    """Workflow for a Customer."""

    entity = 'professional'
    initial_state = 'created'

    created = WorkflowState('created', title='Created', description='Customer created')
    active = WorkflowState('active', title='Professional', description='Customer created')
    inactive = WorkflowState('inactive', title='Professional', description='Customer created')
