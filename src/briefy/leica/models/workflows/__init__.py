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
    created = WorkflowState('created', description='Asset created')
    validation = WorkflowState('validation', title='In Validation',
                               description='Asset under automatic validation')
    rejected = WorkflowState('rejected', title='Rejected', description='Asset Rejected')
    pending = WorkflowState('pending', title='Pending Approval',
                            description='Under verification by internal Q.A.')
    reserved = WorkflowState('reserved', description='Reserved for future use')
    discarded = WorkflowState('discarded', description='')
    post_processing = WorkflowState('post_processing', title='Post Processing',
                                    description='Asset under manual post-processing')
    approved = WorkflowState('approved', description='Ready for delivery')
    delivered = WorkflowState('delivered', description='Delivered to customer')

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

    can_submit = Permission().for_groups('r:professional')
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
        if not self.context or not self.document:
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

    # States
    created = WorkflowState('created',  description='Job created')
    pending = WorkflowState('pending', description='Awaiting professional assignment')
    published = WorkflowState('published', description='Available for Professional Self Assignment')
    scheduling = WorkflowState('scheduling', description='Schedulling date for shooting')
    scheduled = WorkflowState('scheduled', description='Waiting for arranged time for shooting')
    awaiting_assets = WorkflowState('awaiting_assets', title='Awaiting Uploads',
                                    description='Waiting for Photo/Video upload')
    in_qa = WorkflowState('in_qa', title='QA', description='Under Quality Assurance')

    approved = WorkflowState('approved', title='Photoset is ok',
                             description='Photos approved for delivery')
    revision = WorkflowState('Revision', title='Revision', description='Under customer revision')
    completed = WorkflowState('completed', description='Job delivered ok')
    cancelled = WorkflowState('cancelled', description='Job no longer required')

    # Transitions
    submit = created.transition(state_to=pending, permission='can_submit')
    assign = pending.transition(state_to=scheduling, permission='can_assign')
    publish = pending.transition(state_to=published, permission='can_publish')
    retract = published.transition(state_to=pending, permission='can_retract')
    schedule = scheduling.transition(state_to=scheduled, permission='can_schedule')
    scheduling_issues = scheduled.transition(state_to=scheduling,
                                             extra_states=(awaiting_assets,),
                                             permission='can_have_schedulling_issues')
    ready_for_upload = scheduled.transition(state_to=awaiting_assets,
                                            permission='can_get_ready_for_upload')
    upload = awaiting_assets.transition(state_to=in_qa, permission='can_upload')
    reject = in_qa.transition(state_to=awaiting_assets, permission='can_reject')
    approve = in_qa.transition(state_to=approved, permission='can_approve')
    retract_approval = approved.transition(state_to=in_qa, permission='can_retract_approval')
    deliver = approved.transition(state_to=revision, permission='can_deliver')
    customer_reject = revision.transition(state_to=in_qa, permission='can_customer_reject')
    customer_approve = revision.transition(state_to=completed, permission='can_customer_approve')
    cancel = revision.transition(state_to=cancelled, permission='can_cancel')

    can_submit = Permission().for_groups('g:system')
    can_assign = Permission().for_groups('r:scout_manager', 'r:project_manager')
    can_publish = Permission().for_groups('r:scout_manager', 'r:project_manager')
    can_retract = Permission().for_groups('r:scout_manager', 'r:project_manager')
    can_schedule = Permission().for_groups(
        'r:scout_manager', 'r:project_manager', 'r:professional')
    can_have_schedulling_issues = Permission().for_groups(
        'r:scout_manager', 'r:project_manager', 'r:professional')
    can_get_ready_for_upload = Permission().for_groups(
        'r:scout_manager', 'r:professional', 'g:system')
    can_upload = Permission().for_groups('r:professional')
    can_reject = Permission().for_groups('r:qa_manager')
    can_approve = Permission().for_groups('r:qa_manager')
    can_retract_approval = Permission().for_groups('r:qa_manager', 'r:project_manager')
    can_customer_reject = Permission().for_groups('r:customer')
    can_customer_approve = Permission().for_groups('r:customer')
    can_cancel = Permission().for_groups('r:project_manager')


class ProjectWorkflow(BriefyWorkflow):
    """Workflow for a Project."""

    entity = 'projects'
    initial_state = 'created'

    created = WorkflowState('created', title='Created', description='Project created')
