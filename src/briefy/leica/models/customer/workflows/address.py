"""Customer Workflow."""
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import BriefyWorkflow


class BillingAddressWorkflow(BriefyWorkflow):
    """Workflow for a Customer Billing Address."""

    entity = 'customerbillingaddress'
    initial_state = 'created'

    created = WS(
        'created', 'Created',
        'Customer Billing Address created.'
    )
