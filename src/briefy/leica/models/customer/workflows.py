"""Customer Workflow."""
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState as WS

import logging


logger = logging.getLogger(__name__)


class CustomerWorkflow(BriefyWorkflow):
    """Workflow for a Customer."""

    entity = 'customer'
    initial_state = 'created'

    created = WS('created', 'Created')
    """Customer created."""


class BillingAddressWorkflow(BriefyWorkflow):
    """Workflow for a Customer Billing Address."""

    entity = 'customerbillingaddress'
    initial_state = 'created'

    created = WS('created', 'Created')
    """Customer Billing Address created."""


class ContactWorkflow(BriefyWorkflow):
    """Workflow for a Customer Contct ."""

    entity = 'customercontact'
    initial_state = 'created'

    created = WS('created', 'Created')
    """Customer Contact created."""
