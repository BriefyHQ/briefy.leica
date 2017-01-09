"""Customer Workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.vocabularies.roles import LocalRolesChoices as LR
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState as WS

import logging


logger = logging.getLogger(__name__)


class CustomerWorkflow(BriefyWorkflow):
    """Workflow for a Customer."""

    entity = 'customer'
    initial_state = 'created'

    created = WS(
        'created', 'Created',
        'Customer created.'
    )

    pending = WS(
        'pending', 'Pending',
        'A Customer that still needs to close a deal with Briefy.'
    )

    active = WS(
        'active', 'Active',
        'Active Customer.'
    )

    inactive = WS(
        'inactive', 'Inactive',
        'Inactive Customer.'
    )

    # Transitions:
    @created.transition(pending, 'can_submit')
    def submit(self):
        """Submit a new customer to approval."""
        pass

    @pending.transition(active, 'can_activate')
    @inactive.transition(active, 'can_activate')
    def activate(self):
        """Activate a customer."""
        pass

    @pending.transition(inactive, 'can_inactivate')
    @active.transition(inactive, 'can_inactivate')
    def inactivate(self):
        """Inactivate a customer."""
        pass

    @Permission(groups=[LR['owner'], G['bizdev'], ])
    def can_submit(self):
        """Validate if user can submit a profile."""
        return True

    @Permission(groups=[LR['owner'], G['bizdev'], G['finance']])
    def can_activate(self):
        """Validate if user can activate this working location."""
        return True

    @Permission(groups=[LR['owner'], G['bizdev'], G['finance']])
    def can_inactivate(self):
        """Validate if user can inactivate this working location."""
        return True


class BillingAddressWorkflow(BriefyWorkflow):
    """Workflow for a Customer Billing Address."""

    entity = 'customerbillingaddress'
    initial_state = 'created'

    created = WS(
        'created', 'Created',
        'Customer Billing Address created.'
    )


class ContactWorkflow(BriefyWorkflow):
    """Workflow for a Customer Contct ."""

    entity = 'customercontact'
    initial_state = 'created'

    created = WS(
        'created', 'Created',
        'Customer Contact created.'
    )
