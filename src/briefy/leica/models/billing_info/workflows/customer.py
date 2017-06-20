"""Workflow for customer billing information."""
from briefy.leica.models.billing_info.workflows.base import BillingInfoWorkflow


class CustomerBillingInfoWorkflow(BillingInfoWorkflow):
    """Workflow for a CustomerBillingInfoWorkflow."""

    entity = 'customerbillinginfo'
