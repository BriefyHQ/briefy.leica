"""Briefy Lead workflows."""
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState
from briefy.common.workflow import WorkflowTransition


class AssetWorkflow(BriefyWorkflow):
    """Workflow for a Lead."""

    # Optional name for this workflow
    entity = 'lead'
    initial_state = 'created'

    # States
    created = WorkflowState('created', title='Created', description='Asset created')
    staff_action = WorkflowState('staff_action', title='staff_action_required', description='Staff Action Required')
    author_action = WorkflowState('author_action', title='author_action_required', description='Author Action Required')
    aproved = WorkflowState('aproved', title='aproved', description='Asset Aproved')
    rejected = WorkflowState('rejected', title='Rejected', description='Asset Rejected')
    delivered = WorkflowState('delivered', title='delivered', description='Asset Delivered')

    # Transitions
    request_aproval = WorkflowTransition(
        'request_aproval', title='Request Aproval',
        description='', category='',
        state_from=('created', 'author_action'),
        state_to='staff_action',
        permissions='qa scout owner'.split(),
    )



    def __init__(self, name, title='', description='', category='',
                 permission='', state_from=None, state_to=None, **kwargs):
