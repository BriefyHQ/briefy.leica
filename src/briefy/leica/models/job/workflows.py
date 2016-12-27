"""Job workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.vocabularies.roles import LocalRolesChoices as LR
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState as WS
from briefy.leica.utils import transitions

import logging


logger = logging.getLogger(__name__)


class JobWorkflow(BriefyWorkflow):
    """Workflow for a Job."""

    entity = 'job'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Job created by the customer.'
    )

    validation = WS(
        'validation', 'Validation',
        'Under system validation.'
    )

    edit = WS(
        'edit', 'Edit',
        'Customer must edit job in order to be approved.'
    )

    pending = WS(
        'pending', 'Pending',
        'Awaiting professional assignment by Briefy.'
    )

    published = WS(
        'published', 'Job Pool',
        'Available for Professional self assignment.'
    )

    assigned = WS(
        'assigned', 'Assigned',
        'Job assigned, waiting for scheduling.'
    )

    scheduled = WS(
        'scheduled', 'Scheduled',
        'Job scheduled.'
    )

    cancelled = WS(
        'cancelled', 'Cancelled',
        'Job was cancelled by the customer.'
    )

    awaiting_assets = WS(
        'awaiting_assets', 'Awaiting Uploads',
        'Waiting for content to be upload to the system.'
    )

    in_qa = WS(
        'in_qa', 'Quality assurance',
        'Job is under quality assurance.'
    )

    approved = WS(
        'approved', 'Content approved',
        'Content was approved by Briefy quality assurance team'
    )

    refused = WS(
        'refused', 'Customer refused',
        'Job was rejected by the customer.'
    )

    completed = WS(
        'completed', 'Completed',
        'Job is completed.'
    )

    # Transitions
    @created.transition(validation, 'can_submit')
    @edit.transition(validation, 'can_submit')
    def submit(self):
        """After job creation, or edition submit it to machine validation."""
        pass

    @validation.transition(pending, 'can_validate')
    def validate(self):
        """Validate a job."""
        pass

    @validation.transition(edit, 'can_validate')
    def invalidate(self):
        """Invalidate a job, sending it to edit."""
        pass

    @pending.transition(assigned, 'can_assign')
    def assign(self):
        """Assign a Job to a professional."""
        pass

    @pending.transition(published, 'can_publish')
    def publish(self):
        """Put the job to be self assigned."""
        pass

    @published.transition(pending, 'can_retract')
    def retract(self):
        """Remove a job from Job Poll."""
        pass

    @published.transition(assigned, 'can_self_assign')
    def self_assign(self):
        """Professional gets a job."""
        pass

    @assigned.transition(scheduled, 'can_schedule')
    @awaiting_assets.transition(scheduled, 'can_schedule')
    def schedule(self):
        """Professional schedules the job."""
        pass

    @assigned.transition(assigned, 'can_schedule')
    def scheduling_issues(self):
        """Professional reports scheduling issues."""
        pass

    @scheduled.transition(awaiting_assets, 'can_get_ready_for_upload')
    def ready_for_upload(self):
        """System moves job to awaiting for upload."""
        pass

    @awaiting_assets.transition(in_qa, 'can_upload')
    def upload(self):
        """Professional submits all assets for QA."""
        pass

    @in_qa.transition(pending, 'can_unassign')
    def unassign(self):
        """QA unassign a Job."""
        # Update state and comments on Knack
        pass

    @in_qa.transition(approved, 'can_approve')
    def approve(self):
        """QA approves a Job."""
        job = self.document
        if not job.approvable:
            raise self.state.exception_transition(
                'Incorrect number of assets.'
            )
        # Transition all pending assets to approved
        transitions.approve_assets_in_job(job, self.context)

    @in_qa.transition(awaiting_assets, 'can_approve', require_message=True)
    def reject(self):
        """QA rejects a Job."""
        pass

    @approved.transition(in_qa, 'can_retract_approval')
    @refused.transition(in_qa, 'can_retract_approval_customer')
    def retract_approval(self):
        """QA retracts the approval."""
        pass

    @approved.transition(completed, 'can_complete')
    @refused.transition(completed, 'can_complete_from_refused')
    def complete(self):
        """Customer approve the job."""
        pass

    @approved.transition(refused, 'can_refuse', require_message=True)
    def refuse(self):
        """Customer refuses the job."""
        pass

    @approved.transition(approved, 'can_deliver')
    def deliver(self):
        """Execute the delivery of job assets."""
        pass

    @pending.transition(cancelled, 'can_cancel')
    @published.transition(cancelled, 'can_cancel')
    @assigned.transition(cancelled, 'can_cancel')
    @scheduled.transition(scheduled, 'can_cancel')
    def cancel(self):
        """Customer or Briefy cancel the job.."""
        pass

    @Permission(groups=[G['customers'], G['bizdev'], G['system']])
    def can_submit(self):
        """Validate if user can submit the job."""
        return True

    @Permission(groups=[G['scout'], G['pm']])
    def can_assign(self):
        """Validate if user can assign the job to a professional."""
        return True

    @Permission(groups=[G['professionals'], ])
    def can_self_assign(self):
        """Validate if user is able to self assign this job."""
        # TODO: Check for existing jobs in the same date.
        return True

    @Permission(groups=[G['system'], ])
    def can_validate(self):
        """Validate if user is system and job."""
        return True

    @Permission(groups=[G['customers'], G['pm'], G['scout'], G['system']])
    def can_publish(self):
        """Validate if user can publish this job (job pool)."""
        return True

    @Permission(groups=[G['customers'], G['pm'], G['scout']])
    def can_retract(self):
        """Validate if user can retract job from job pool."""
        return True

    @Permission(groups=[G['professionals'], G['pm']])
    def can_schedule(self):
        """Validate if user can schedule a job."""
        return True

    @Permission(groups=[G['system'], ])
    def can_get_ready_for_upload(self):
        """Validate if user can move Job to waiting for assets."""
        return True

    @Permission(groups=[G['professionals'], G['qa'], ])
    def can_upload(self):
        """Validate if user can move Job to qa."""
        return True

    @Permission(groups=[LR['qa_manager'], G['qa'], G['pm'], ])
    def can_unassign(self):
        """Validate if user can unassign a Job."""
        return True

    @Permission(groups=[LR['qa_manager'], G['qa'], ])
    def can_approve(self):
        """Validate if user can approve a Job."""
        return True

    @Permission(groups=[LR['qa_manager'], G['qa'], ])
    def can_reject(self):
        """Validate if user can reject a Job."""
        return True

    @Permission(groups=[LR['qa_manager'], G['qa'], ])
    def can_retract_approval(self):
        """Validate if user can retract an approval."""
        return True

    @Permission(groups=[LR['qa_manager'], G['qa'], G['pm']])
    def can_retract_approval_customer(self):
        """Validate if user can retract from customer_retract."""
        return True

    @Permission(groups=[G['customers'], G['pm'], G['system']])
    def can_complete(self):
        """Validate if user can move a job to completed."""
        return True

    @Permission(groups=[G['customers'], G['pm']])
    def can_complete_from_refused(self):
        """Validate if user can move a job to completed from refused state."""
        return True

    @Permission(groups=[G['customers'], ])
    def can_refuse(self):
        """Validate if user can reject a job as a customer."""
        return True

    @Permission(groups=[G['customers'], ])
    def can_cancel(self):
        """Validate if user can cancel a job as a customer."""
        return True

    @Permission(groups=[G['system'], ])
    def can_deliver(self):
        """Validate if user can execute a deliver transition."""
        return True


class JobLocationWorkflow(BriefyWorkflow):
    """Workflow for a JobLocation."""

    entity = 'joblocation'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Job Location inserted on the database.'
    )


class JobOrderWorkflow(BriefyWorkflow):
    """Workflow for a JobOrder."""

    entity = 'joborder'
    initial_state = 'received'

    # States
    received = WS(
        'received', 'Received',
        'Job Order received to be executed.'
    )

    assigned = WS(
        'assigned', 'Assigned',
        'Job Order assigned to a Professional.'
    )

    scheduled = WS(
        'scheduled', 'Scheduled',
        'Job Order scheduled to be executed.'
    )

    in_qa = WS(
        'in_qa', 'In QA',
        'Job Order in the quality assurance validation.'
    )

    cancelled = WS(
        'cancelled', 'Cancelled',
        'Job Order cancelled.'
    )

    delivered = WS(
        'delivered', 'Delivered',
        'Job Order delivered by quality assurance.'
    )

    accepted = WS(
        'accepted', 'Accepted',
        'Job Order accepted by the customer.'
    )

    refused = WS(
        'refused', 'Refused',
        'Job Order refused by the customer.'

    )

    perm_refused = WS(
        'perm_refused', 'Permanently Refused',
        'Job Order permanently refused.'

    )

    # Transitions
    @received.transition(assigned, 'can_assign')
    def assign(self):
        """Transition: Assign a professional to the JobOder."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], G['scout'], ])
    def can_assign(self):
        """Permission: Validate if user can assign a JobOrder.

        Groups: g:pm, g:scout, r:project_manager
        """
        return True

    @received.transition(scheduled, 'can_self_assign')
    def self_assign(self):
        """Transition: Professional self assign the JobOrder."""
        pass

    @Permission(groups=[G['professionals'], ])
    def can_self_assign(self):
        """Permission: Validate if user can self assign a JobOrder.

        Groups: g:professionals
        """
        return True

    @scheduled.transition(cancelled, 'can_cancel')
    @assigned.transition(cancelled, 'can_cancel')
    @received.transition(cancelled, 'can_cancel')
    def cancel(self):
        """Transition: Cancel the JobOrder."""
        pass

    @Permission(groups=[LR['project_manager'], LR['customer_user'], G['pm'], G['customers'], ])
    def can_cancel(self):
        """Permission: Validate if user can move the JobOrder to the cancelled state.

        Groups: g:pm, g:customers, r:project_manager, r:customer_user
        """
        # TODO: validate if the restrictions before cancel the JobOrder
        return True

    @assigned.transition(scheduled, 'can_schedule')
    def schedule(self):
        """Transition: Inform the schedule to the customer."""
        pass

    @Permission(groups=[LR['project_manager'], LR['professional_user'], G['pm'], G['scout']])
    def can_schedule(self):
        """Permission: Validate if user can schedule a JobOrder.

        Groups: g:pm, g:scout, r:project_manager, r:professional_user
        """
        return True

    @scheduled.transition(in_qa, 'can_start_qa')
    def start_qa(self):
        """Transition: Inform the start of QA to the customer."""
        pass

    @Permission(groups=[G['system'], G['qa'], ])
    def can_start_qa(self):
        """Permission: Validate if user can move JobOrder the in_qa state.

        Groups: g:system, g:qa
        """
        return True

    @in_qa.transition(delivered, 'can_deliver')
    def deliver(self):
        """Transition: Inform the deliver of the JobOrder to the customer."""
        pass

    @Permission(groups=[LR['qa_manager'], G['qa'], G['system'], ])
    def can_deliver(self):
        """Permission: Validate if user can deliver the JobOrder.

        Groups: g:qa, g:system, r:qa_manager
        """
        return True

    @delivered.transition(refused, 'can_refuse')
    def refuse(self):
        """Transition: Customer refuse the JobOrder."""
        pass

    @Permission(groups=[G['pm'], G['customers'], LR['project_manager'], LR['customer_user'], ])
    def can_refuse(self):
        """Permission: Validate if user can refuse the JobOrder.

        Groups: g:pm, g:customers, r:customer_user, r:project_manager
        """
        return True

    @in_qa.transition(received, 'can_reshoot')
    @in_qa.transition(assigned, 'can_reshoot')
    @refused.transition(received, 'can_reshoot')
    @refused.transition(assigned, 'can_reshoot')
    def reshoot(self):
        """Transition: Inform the reshoot of the JobOrder the customer."""
        pass

    @Permission(groups=[LR['project_manager'], LR['qa_manager'], G['pm'], G['qa'], ])
    def can_reshoot(self):
        """Permission: Validate if user reshoot a JobOrder.

        Groups: g:pm, g:qa, r:qa_manager, r:project_manager
        """
        return True

    @delivered.transition(accepted, 'can_accept')
    def accept(self):
        """Transition: Customer or PM accept the JobOrder."""
        pass

    @Permission(groups=[G['pm'], G['customers'], G['system'], LR['project_manager'], LR['customer_user'], ])
    def can_accept(self):
        """Permission: Validate if user can accept the JobOrder.

        Groups: g:pm, g:customers, g:system, r:customer_user, r:project_manager
        """
        return True

    @refused.transition(perm_refused, 'can_perm_refuse')
    def perm_refuse(self):
        """Transition: PM permanently refuse the JobOrder."""
        pass

    @Permission(groups=[G['pm'], G['bizdev'], LR['project_manager'], ])
    def can_perm_refuse(self):
        """Permission: Validate if user can permanently refuse the JobOrder.

        Groups: g:pm, g:bizdev, r:project_manager
        """
        return True

    @refused.transition(in_qa, 'can_require_revision')
    def require_revision(self):
        """Transition: PM or Customer require revision of the JobOrder."""
        pass

    @Permission(groups=[G['pm'], G['customers'], LR['project_manager'], LR['customer_user'] ])
    def can_require_revision(self):
        """Permission: Validate if user can require revision of the JobOrder.

        Groups: g:pm, g:customers, r:project_manager, r:customer_user
        """
        return True
