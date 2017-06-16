"""Workflow for professional billing information."""
from briefy.leica.models.billing_info.workflows.base import BillingInfoWorkflow


class ProfessionalBillingInfoWorkflow(BillingInfoWorkflow):
    """Workflow for a ProfessionalBillingInfoWorkflow."""

    entity = 'professionalbillinginfo'
