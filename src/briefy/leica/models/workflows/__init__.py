"""Briefy Leica workflows."""
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState


class AssetWorkflow(BriefyWorkflow):
    """Workflow for an Asset."""

    # Optional name for this workflow
    entity = 'asset'
    initial_state = 'created'

    # States:
    created = WorkflowState('created', title='Created', description='Asset created')
    validation = WorkflowState('validation', title='In Validation',
                               description='Asset under automatic validation')
    rejected = WorkflowState('rejected', title='Rejected', description='Asset Rejected')
    pending = WorkflowState('pending', title='Pending Approval',
                            description='Under verification by internal Q.A.')
    reserved = WorkflowState('reserved', title='Reserved', description='Reserved for future use')
    discarded = WorkflowState('discarded', title='Discarded', description='')
    post_processing = WorkflowState('post_processing', title='Post Processing',
                                    description='Asset under manual post-processing')
    approved = WorkflowState('approved', title='Approved', description='Ready for delivery')
    delivered = WorkflowState('delivered', title='Delivered', description='Delivered to customer')

    # Transitions:
    submit = created.transition(state_to=validation, permission='can_submit',
                                extra_states=(rejected,))
    invalidate = validation.transition(state_to=rejected, permission='can_invalidate',
                                       title='Invalidate')
    validate = validation.transition(state_to=pending, permission='can_validate',
                                     extra_states=(rejected,))

    discard = pending.transition(state_to=discarded, permission='can_discard',
                                 extra_states=(delivered,))
    process = pending.transition(state_to=post_processing, permission='can_start_processing')
    reserve = pending.transition(state_to=reserved, permission='can_reserve')
    reject = pending.transition(state_to=rejected, permission='can_reject')

    approve = pending.transition(state_to=approved, permission='can_approve')

    retract = approved.transition(state_to=pending, permission='can_retract',
                                  extra_states=(discarded, reserved,))
    deliver = approved.transition(state_to=delivered, permission='can_deliver',)
    processed = post_processing.transition(state_to=pending, permission='can_end_processing')

    # Permissions:
    can_submit = Permission().for_groups('g:professionals')
    can_invalidate = Permission().for_groups('g:system')
    can_discard = Permission().for_groups('g:briefy_qa')

    can_reserve = Permission().for_groups('g:briefy_qa')
    can_approve = Permission().for_groups('g:briefy_qa')
    can_start_processing = Permission().for_groups('g:briefy_qa')
    can_reserve = Permission().for_groups('g:briefy_qa')
    can_reject = Permission().for_groups('g:briefy_qa')
    can_retract = Permission().for_groups('g:briefy_qa')
    can_deliver = Permission().for_groups('g:system')
    can_end_processing = Permission().for_groups('g:briefy_qa')

    @Permission
    def can_validate(self):
        if not self.context or not self.context:
            return False
        if self.state is self.validation and 'g:system' in self.context.groups:
            return True
        if self.state is self.rejected and 'g:briefy_qa' in self.context.groups:
            return True
        return False


class CustomerWorkflow(BriefyWorkflow):
    """Workflow for a Customer."""

    entity = 'customers'
    initial_state = 'created'

    created = WorkflowState('created', title='Created', description='Customer created')


class CommentWorkflow(BriefyWorkflow):
    """Workflow for a Comment."""

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
