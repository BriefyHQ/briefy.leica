"""Order workflow."""
from briefy.leica.models.job.workflows.base import BaseOrderWorkflow


class OrderWorkflow(BaseOrderWorkflow):
    """Workflow for an Order."""

    entity = 'order'
