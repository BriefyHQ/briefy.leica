"""Briefy Leica workflows."""
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState
from briefy.common.workflow import WorkflowTransition


class AssetWorkflow(BriefyWorkflow):
    """Workflow for an Asset."""

    # Optional name for this workflow
    entity = 'asset'
    initial_state = 'created'

    # States
    created = WorkflowState('created', title='Created', description='Asset created')
    staff_action = WorkflowState(
        'staff_action', title='staff_action_required', description='Staff Action Required'
    )
    author_action = WorkflowState(
        'author_action', title='author_action_required', description='Author Action Required'
    )
    aproved = WorkflowState('aproved', title='aproved', description='Asset Aproved')
    rejected = WorkflowState('rejected', title='Rejected', description='Asset Rejected')
    delivered = WorkflowState('delivered', title='delivered', description='Asset Delivered')

    # Transitions
    request_aproval = WorkflowTransition(
        name='request_aproval', title='Request Aproval',
        description='', category='',
        state_from=created,
        state_to=staff_action,
        permissions='qa scout owner'.split(),
    )
    request_review = WorkflowTransition(
        name='request_review', title='Request Review',
        description='', category='',
        state_from=staff_action,
        state_to=author_action,
        permissions='qa scout owner'.split(),
    )
    # aprove = WorkflowTransition(
    #     'request_review', title='Request Review',
    #     description='', category='',
    #     state_from= 'staff_action',
    #     state_to='author_action',
    #     permissions='qa scout owner'.split(),
    # )


class CommentWorkflow(BriefyWorkflow):
    """Workflow for an Comment."""

    entity = 'comments'
    initial_state = 'created'

    created = WorkflowState('created', title='Created', description='Comment created')


class JobWorkflow(BriefyWorkflow):
    """Workflow for an Asset."""

    entity = 'jobs'
    initial_state = 'created'

    created = WorkflowState('created', title='Created', description='Asset created')
    aproved = WorkflowState('photoset_is_ok', title='Photoset is ok',
                            description='Photos aproved for delivery')


class ProjectWorkflow(BriefyWorkflow):
    """Workflow for a Project."""

    entity = 'projects'
    initial_state = 'created'

    created = WorkflowState('created', title='Created', description='Project created')
