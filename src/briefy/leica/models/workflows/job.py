"""Job workflow."""
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState
from briefy.leica import internal_actions
from briefy.leica.models.workflows.utils import G_CUS
from briefy.leica.models.workflows.utils import G_PM
from briefy.leica.models.workflows.utils import G_PROF
from briefy.leica.models.workflows.utils import G_QA
from briefy.leica.models.workflows.utils import G_SCOUT
from briefy.leica.models.workflows.utils import G_SYS
from briefy.leica.models.workflows.utils import R_QA
from briefy.leica.utils import bridge
from briefy.leica.utils import transitions

import logging


logger = logging.getLogger(__name__)


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
    def approve(self, *args, **kwargs):
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
    def reject(self, workflow, *args, **kwargs):
        """Reject a Job."""
        # Update state and comments on Knack
        job = self.document
        job_info = bridge.get_info_from_job(job)
        internal_actions.submit(bridge.reject_job, job_info)

    func = Permission().for_groups
    # TODO: review permission
    can_submit = func(G_SYS, G_QA)
    can_assign = func(G_SCOUT, G_PM)
    can_publish = func(G_SCOUT, G_PM)
    can_retract = func(G_SCOUT, G_PM)
    can_schedule = func(G_SCOUT, G_PM, G_PROF)
    can_have_schedulling_issues = func(G_SCOUT, G_PM, G_PROF)
    can_get_ready_for_upload = func(G_SCOUT, G_PROF, G_SYS)
    can_upload = func(G_PROF)
    can_reject = func(R_QA, G_QA)
    # TODO: review permission
    can_approve = func(R_QA, G_QA)
    can_retract_approval = func(R_QA, G_PM, G_QA)
    can_customer_reject = func(G_CUS)
    can_customer_approve = func(G_CUS)
    can_cancel = func(G_PM)
    # TODO: in the future this should be changed to a context role
    can_self_assign = func(G_PROF)
    can_workaround = func(G_QA, G_PM)
