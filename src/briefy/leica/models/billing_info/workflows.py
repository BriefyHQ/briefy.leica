"""Billing information workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.vocabularies.roles import LocalRolesChoices as LR
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission


class BillingInfoWorkflow(BriefyWorkflow):
    """Workflow for a BillingInfo."""

    entity = 'billinginfo'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Inserted into the database.'
    )

    deleted = WS(
        'deleted', 'Deleted link',
        'Billing info was deleted from the platform.'
    )

    # Transitions:
    @created.transition(deleted, 'can_delete')
    def delete(self):
        """Delete a info."""
        pass

    @Permission(groups=[LR['owner'], G['finance'], G['scout']])
    def can_delete(self):
        """Validate if user can delete this info."""
        return True


class CustomerBillingInfoWorkflow(BillingInfoWorkflow):
    """Workflow for a CustomerBillingInfoWorkflow."""

    entity = 'customerbillinginfo'


class ProfessionalBillingInfoWorkflow(BillingInfoWorkflow):
    """Workflow for a ProfessionalBillingInfoWorkflow."""

    entity = 'professionalbillinginfo'
