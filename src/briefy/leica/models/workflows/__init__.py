"""Briefy Leica workflows."""
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState
from briefy.leica import internal_actions
from briefy.leica.utils import bridge
from briefy.leica.utils import transitions

import logging


logger = logging.getLogger(__name__)


class AssetWorkflow(BriefyWorkflow):
    """Workflow for an Asset."""

    # Optional name for this workflow
    entity = 'asset'
    initial_state = 'created'

    # States:
    created = WorkflowState('created', description='Asset created')
    edit = WorkflowState('edit', description='Request asset edit')
    validation = WorkflowState('validation', title='In Validation',
                               description='Asset under automatic validation')
    rejected = WorkflowState('rejected', title='Rejected', description='Asset Rejected')
    pending = WorkflowState('pending', title='Pending Approval',
                            description='Under verification by internal Q.A.')
    reserved = WorkflowState('reserved', description='Reserved for future use')
    post_processing = WorkflowState('post_processing', title='Post Processing',
                                    description='Asset under manual post-processing')
    approved = WorkflowState('approved', description='Ready for delivery')
    delivered = WorkflowState('delivered', description='Delivered to customer')

    # Transitions:
    submit = created.transition(state_to=validation, permission='can_submit',
                                extra_states=(edit,))
    invalidate = validation.transition(state_to=edit, permission='can_validate',
                                       title='Invalidate')
    validate = validation.transition(state_to=pending, permission='can_validate',
                                     extra_states=(edit,))

    discard = pending.transition(state_to=rejected, permission='can_discard',
                                 extra_states=(delivered,))
    process = pending.transition(state_to=post_processing, permission='can_start_processing')
    reserve = pending.transition(state_to=reserved, permission='can_reserve',
                                 extra_states=(approved,))
    reject = pending.transition(state_to=edit, permission='can_reject')

    approve = pending.transition(state_to=approved, permission='can_approve',
                                 extra_states=(reserved,))
    retract = approved.transition(state_to=pending, permission='can_retract',
                                  extra_states=(rejected, reserved,))
    deliver = approved.transition(state_to=delivered, permission='can_deliver',)
    processed = post_processing.transition(state_to=pending, permission='can_end_processing')

    # Permissions:

    can_submit = Permission().for_groups('g:professionals', 'g:briefy_qa')
    can_invalidate = Permission().for_groups('g:system', 'g:professionals', 'g:briefy_qa')
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
        allowed_groups = ['g:system', 'g:briefy_qa']
        is_right_state = False
        if self.state.name == self.edit.name:
            is_right_state = True
        elif self.state.name == self.validation.name:
            is_right_state = True
            allowed_groups.extend(['g:professionals')
        user_has_role = [p for p in allowed_groups if p in self.context.groups]
        return is_right_state and user_has_role


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
    workaround_upload = pending.transition(state_to=awaiting_assets, permission='can_workaround')
    workaround_qa = pending.transition(state_to=in_qa, permission='can_workaround')

    retract = published.transition(state_to=pending, permission='can_retract')
    self_assign = published.transition(state_to=scheduling, permission='can_self_assign')

    schedule = scheduling.transition(state_to=scheduled, permission='can_schedule')
    scheduling_issues = scheduled.transition(state_to=scheduling,
                                             extra_states=(awaiting_assets,),
                                             permission='can_have_schedulling_issues')
    ready_for_upload = scheduled.transition(state_to=awaiting_assets,
                                            permission='can_get_ready_for_upload')
    upload = awaiting_assets.transition(state_to=in_qa, permission='can_upload')
    retract_approval = approved.transition(state_to=in_qa, permission='can_retract_approval')
    deliver = approved.transition(state_to=revision, permission='can_deliver')
    customer_reject = revision.transition(state_to=in_qa, permission='can_customer_reject')
    customer_approve = revision.transition(state_to=completed, permission='can_customer_approve')
    cancel = revision.transition(state_to=cancelled, permission='can_cancel')
    reject = in_qa.transition(state_to=awaiting_assets, permission='can_reject')
    approve = in_qa.transition(state_to=approved, permission='can_approve')

    @approve
    def approve_transition(self, *args, **kwargs):
        """Approve a Job."""
        job = self.document
        if not job.approvable:
            raise self.state.exception_transition(
                'Incorrect number of assets.'
            )
        # Transition all pending assets to approved
        transitions.approve_assets_in_job(job, self.context)
        job_info = bridge.get_info_from_job(job)
        # Update state and comments on Knack
        internal_actions.submit(bridge.approve_job, job_info)

    @reject
    def reject_transition(self, workflow, *args, **kwargs):
        """Reject a Job."""
        # Update state and comments on Knack
        job = self.document
        job_info = bridge.get_info_from_job(job)
        internal_actions.submit(bridge.reject_job, job_info)

    # TODO: review permission
    can_submit = Permission().for_groups('g:system', 'g:briefy_qa')
    can_assign = Permission().for_groups('g:briefy_scout', 'g:briefy_pm')
    can_publish = Permission().for_groups('g:briefy_scout', 'g:briefy_pm')
    can_retract = Permission().for_groups('g:briefy_scout', 'g:briefy_pm')
    can_schedule = Permission().for_groups(
        'g:briefy_scout', 'g:briefy_pm', 'g:professionals')
    can_have_schedulling_issues = Permission().for_groups(
        'g:briefy_scout', 'g:briefy_pm', 'g:professionals')
    can_get_ready_for_upload = Permission().for_groups(
        'g:briefy_scout', 'g:professionals', 'g:system')
    can_upload = Permission().for_groups('g:professionals')
    can_reject = Permission().for_groups('r:qa_manager', 'g:briefy_qa')
    # TODO: review permission
    can_approve = Permission().for_groups('r:qa_manager', 'g:briefy_qa')
    can_retract_approval = Permission().for_groups('r:qa_manager', 'g:briefy_pm',
                                                   'g:briefy_qa')
    can_customer_reject = Permission().for_groups('g:customers')
    can_customer_approve = Permission().for_groups('g:customers')
    can_cancel = Permission().for_groups('g:briefy_pm')
    # TODO: in the future this should be changed to a context role
    can_self_assign = Permission().for_groups('g:professionals')
    can_workaround = Permission().for_groups('g:briefy_qa')


class ProfessionalWorkflow(BriefyWorkflow):
    """Workflow for a Customer."""

    entity = 'professional'
    initial_state = 'created'

    created = WorkflowState('created', title='Created', description='Customer created')
    active = WorkflowState('active', title='Professional', description='Customer created')
    inactive = WorkflowState('inactive', title='Professional', description='Customer created')


class ProjectWorkflow(BriefyWorkflow):
    """Workflow for a Project."""

    entity = 'projects'
    initial_state = 'created'

    created = WorkflowState('created', title='Created', description='Project created')
