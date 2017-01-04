"""Job workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.vocabularies.roles import LocalRolesChoices as LR
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState as WS
from briefy.leica.utils import transitions

import logging


logger = logging.getLogger(__name__)


class JobAssignmentWorkflow(BriefyWorkflow):
    """Workflow for a Job Assignment."""

    entity = 'job'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Assignment created.'
    )

    pending = WS(
        'pending', 'Pending',
        'Awaiting professional assignment by Briefy or availability dates from customer.'
    )

    published = WS(
        'published', 'Job Pool',
        'Available for Professional self assignment using Job pool.'
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
        'Job was cancelled by the customer or pm.'
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
        'Content was approved by Briefy quality assurance team.'
    )

    refused = WS(
        'refused', 'Customer refused',
        'Job was rejected by the customer.'
    )

    # TODO: "completed" belongs to JobOrderWorkflow
    completed = WS(
        'completed', 'Completed',
        'Assignment is completed.'
    )

    perm_rejected = WS(
        'perm_rejected', 'Permanently Rejected',
        'Assignment was permanently rejected by QA.'
    )

    asset_validation = WS(
        'asset_validation', 'Asset Validation',
        'Assignment is awaiting automatic asset validation.'
    )

    # Transitions

    @created.transition(pending, 'can_submit')
    def submit(self):
        """Submit Assignment."""
        pass

    @Permission(groups=[G['customers'], G['pm'], G['bizdev'], G['system'], ])
    def can_submit(self):
        """Validate if user can submit an Assignment."""
        return True

    @pending.transition(assigned, 'can_assign')
    def assign(self):
        """Define a Professional to the Assignment."""
        pass

    @Permission(groups=[G['scout'], G['pm'], ])
    def can_assign(self):
        """Validate if user can set the Professional in the Assignment."""
        return True

    @pending.transition(published, 'can_publish')
    def publish(self):
        """Inform availability dates and move the enable Assignment to be self assigned."""
        pass

    @Permission(groups=[G['customers'], G['pm'], G['scout'], G['system'], ])
    def can_publish(self):
        """Validate if user can publish this job (job pool)."""
        return True

    @published.transition(pending, 'can_retract')
    def retract(self):
        """Remove availability dates and return Assignment to pending."""
        pass

    @Permission(groups=[G['customers'], G['pm'], G['scout'], ])
    def can_retract(self):
        """Validate if user can retract job from job pool."""
        return True

    @published.transition(assigned, 'can_self_assign')
    def self_assign(self):
        """Professional choose the Assignment from the Pool."""
        pass

    @Permission(groups=[G['professionals'], G['pm'], G['scout'], ])
    def can_self_assign(self):
        """Validate if user is able to self assign this job."""
        # TODO: Check for existing jobs in the same date.
        return True

    @assigned.transition(scheduled, 'can_schedule')
    def schedule(self):
        """Professional, Scout or PM schedule the Assignment."""
        pass

    @Permission(groups=[G['professionals'], G['pm'], G['scout'], ])
    def can_schedule(self):
        """Validate if user can schedule an Assignment."""
        return True

    @awaiting_assets.transition(scheduled, 'can_reschedule')
    @scheduled.transition(scheduled, 'can_reschedule')
    def reschedule(self):
        """Professional or PM reschedule an Assignment."""
        pass

    @assigned.transition(assigned, 'can_reschedule')
    def scheduling_issues(self):
        """Professional or PM reports scheduling issues."""
        pass

    @Permission(groups=[G['professionals'], G['pm']])
    def can_reschedule(self):
        """Validate if user can reschedule an Assignment."""
        return True

    @scheduled.transition(assigned, 'can_remove_schedule')
    def remove_schedule(self):
        """Customer, Professional or PM removes the Assignment scheduled shoot datetime."""
        pass

    @Permission(groups=[G['professionals'], G['customers'], G['pm']])
    def can_remove_reschedule(self):
        """Validate if user can remove schedule shoot date time of an Assignment."""
        return True

    @awaiting_assets.transition(cancelled, 'can_cancel')
    @pending.transition(cancelled, 'can_cancel')
    @published.transition(cancelled, 'can_cancel')
    @assigned.transition(cancelled, 'can_cancel')
    @scheduled.transition(cancelled, 'can_cancel')
    def cancel(self):
        """Customer or PM cancel the Assignment."""
        pass

    @Permission(groups=[G['customers'], G['pm'], G['qa'], ])
    def can_cancel(self):
        """Validate if user can cancel an Assignment."""
        # TODO: block cancel if is in awaiting assets after being reject first
        return True

    @scheduled.transition(awaiting_assets, 'can_get_ready_for_upload')
    def ready_for_upload(self):
        """System moves Assignment to awaiting assets (upload)."""
        pass

    @Permission(groups=[G['system'], ])
    def can_get_ready_for_upload(self):
        """Validate if user can move an Assignment from scheduled to waiting for assets."""
        return True

    @awaiting_assets.transition(in_qa, 'can_approve')
    def retract_rejection(self):
        """QA retract rejection or manually move to QA."""
        pass

    @in_qa.transition(approved, 'can_approve')
    def approve(self):
        """QA approves the Assignment Set."""
        job = self.document
        if not job.approvable:
            raise self.state.exception_transition(
                'Incorrect number of assets.'
            )
        # Transition all pending assets to approved
        transitions.approve_assets_in_job(job, self.context)

    @in_qa.transition(awaiting_assets, 'can_approve', require_message=True)
    def reject(self):
        """QA rejects Assignment Set."""
        pass

    @in_qa.transition(perm_rejected, 'can_approve')
    def perm_reject(self):
        """QA permanently reject the Assignment Set."""
        pass

    @approved.transition(in_qa, 'can_approve')
    def retract_approval(self):
        """QA retracts the approval."""
        pass


    @Permission(groups=[LR['qa_manager'], G['qa'], ])
    def can_approve(self):
        """Validate if user can approve or reject an Assignment Set."""
        return True

    @awaiting_assets.transition(asset_validation, 'can_upload')
    def upload(self):
        """Professional submits all assets for QA."""
        pass

    @Permission(groups=[G['professionals'], G['qa'], G['pm'], ])
    def can_upload(self):
        """Validate if user can update submission link and move an Assignment to QA."""
        return True

    @asset_validation.transition(in_qa, 'can_validate_assets')
    def validate_assets(self):
        """System validate uploaded Assets."""
        pass

    @asset_validation.transition(awaiting_assets, 'can_validate_assets')
    def invalidate_assets(self):
        """System invalidate uploaded Assets."""
        pass

    @Permission(groups=[G['system'], ])
    def can_validate_assets(self):
        """Validate if the user can automatic validate /invalidate Assets from an Assignment Set."""
        return True

    @refused.transition(in_qa, 'can_return_to_qa')
    def return_to_qa(self):
        """PM move Assignment back to QA for further revision."""
        pass

    @Permission(groups=[G['pm'], ])
    def can_return_to_qa(self):
        """Validate if the user can return to QA (futher revision) an Assignment Set."""
        return True

    @approved.transition(completed, 'can_complete')
    @refused.transition(completed, 'can_complete')
    def complete(self):
        """Customer, System or PM accept the Assignment Set."""
        pass

    @Permission(groups=[G['customers'], G['pm'], G['system']])
    def can_complete(self):
        """Validate if user can move an Assignment to completed."""
        return True

    @approved.transition(refused, 'can_refuse', require_message=True)
    def refuse(self):
        """Customer or PM refuses the Assignment Set."""
        pass

    @Permission(groups=[G['customers'], G['pm'], ])
    def can_refuse(self):
        """Validate if user can refuse an Assignment Set."""
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
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Order created.'
    )

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
    @created.transition(received, 'can_submit')
    def submit(self):
        """Submit Order."""
        pass

    @Permission(groups=[G['customers'], G['pm'], G['bizdev'], G['system'], ])
    def can_submit(self):
        """Validate if user can submit an JobOrder."""
        return True

    @received.transition(assigned, 'can_assign')
    def assign(self):
        """Transition: Assign a professional to the JobOrder."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], G['scout'], ])
    def can_assign(self):
        """Permission: Validate if user can assign a JobOrder.

        Groups: g:pm, g:scout, r:project_manager
        """
        return True

    @assigned.transition(received, 'can_unassign')
    @scheduled.transition(received, 'can_unassign')
    def unassign(self):
        """Transition: Inform the unassignment to the customer."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], ])
    def can_unassign(self):
        """Permission: Validate if user can unassign a JobOrder.

        Groups: g:pm, r:project_manager
        """
        return True

    @assigned.transition(received, 'can_remove_availability')
    @scheduled.transition(received, 'can_remove_availability')
    def remove_availability(self):
        """Transition: Inform the removal of availability dates to the customer."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], LR['customer_user'], G['customers'], ])
    def can_remove_availability(self):
        """Permission: Validate if user can remove availability dates of a JobOrder.

        Groups: g:pm, r:project_manager, g:customers, r:customer_user
        """
        # TODO: make sure customer only unassign
        return True

    @assigned.transition(assigned, 'can_reassign')
    @scheduled.transition(assigned, 'can_reassign')
    def reassign(self):
        """Transition: Inform the reassignment to the customer."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], ])
    def can_reassign(self):
        """Permission: Validate if user can reassign a JobOrder.

        Groups: g:pm, r:project_manager
        """
        return True

    @scheduled.transition(assigned, 'can_remove_schedule')
    def remove_schedule(self):
        """Transition: Inform the removal of the schedule shoot datetime to the customer."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], G['professionals'], G['customers'], ])
    def can_remove_schedule(self):
        """Permission: Validate if user can remove the schedule of a JobOrder.

        Groups: g:pm, r:project_manager
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

    @received.transition(scheduled, 'can_schedule')
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

    @in_qa.transition(assigned, 'can_reshoot')
    @refused.transition(assigned, 'can_reshoot')
    def reshoot(self):
        """Transition: Inform the reshoot of the JobOrder the customer."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], G['qa'], ])
    def can_reshoot(self):
        """Permission: Validate if user reshoot JobOrder.

        Groups: g:pm, r:project_manager
        """
        return True

    @in_qa.transition(received, 'can_new_shoot')
    @refused.transition(received, 'can_new_shoot')
    def new_shoot(self):
        """Transition: Inform the new shoot of the JobOrder the customer."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], G['qa'], ])
    def can_new_shoot(self):
        """Permission: Validate if user reshoot JobOrder.

        Groups: g:pm, g:customers, r:project_manager, r:customer_user
        """
        return True

    @delivered.transition(accepted, 'can_accept')
    def accept(self):
        """Transition: Customer or PM accept the JobOrder."""
        pass

    @Permission(
        groups=[G['pm'], G['customers'], G['system'], LR['project_manager'], LR['customer_user'], ]
    )
    def can_accept(self):
        """Permission: Validate if user can accept the JobOrder.

        Groups: g:pm, g:customers, g:system, r:customer_user, r:project_manager
        """
        return True

    @refused.transition(perm_refused, 'can_perm_refuse')
    def perm_refuse(self):
        """Transition: PM permanently refuse the JobOrder."""
        pass

    @Permission(groups=[G['pm'], G['bizdev'], LR['project_manager']])
    def can_perm_refuse(self):
        """Permission: Validate if user can permanently refuse the JobOrder.

        Groups: g:pm, g:bizdev, r:project_manager
        """
        return True

    @refused.transition(in_qa, 'can_require_revision')
    def require_revision(self):
        """Transition: PM or Customer require revision of the JobOrder."""
        pass

    @Permission(groups=[G['pm'], G['customers'], LR['project_manager'], LR['customer_user']])
    def can_require_revision(self):
        """Permission: Validate if user can require revision of the JobOrder."""
        return True
