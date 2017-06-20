"""Order Location workflow."""
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import BriefyWorkflow


class OrderLocationWorkflow(BriefyWorkflow):
    """Workflow for a OrderLocation."""

    entity = 'orderlocation'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'OrderLocation inserted on the database.'
    )
