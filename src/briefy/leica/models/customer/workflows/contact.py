"""Customer Contact Workflow."""
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import BriefyWorkflow


class ContactWorkflow(BriefyWorkflow):
    """Workflow for a Customer Contact."""

    entity = 'customercontact'
    initial_state = 'created'

    created = WS(
        'created', 'Created',
        'Customer Contact created.'
    )
