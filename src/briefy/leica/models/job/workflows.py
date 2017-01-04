"""Order, OrderLocation, Assignment and Pool related workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.vocabularies.roles import LocalRolesChoices as LR
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState as WS
from briefy.leica.utils import transitions

import logging


logger = logging.getLogger(__name__)


class AssignmentWorkflow(BriefyWorkflow):
    """Workflow for a Assignment."""

    entity = 'assignment'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Assignment created by the customer.'
    )

    validation = WS(
        'validation', 'Validation',
        'Under system validation.'
    )

    edit = WS(
        'edit', 'Edit',
        'Customer must edit assignment in order to be approved.'
    )

    pending = WS(
        'pending', 'Pending',
        'Awaiting Professional assignment by Briefy.'
    )

    published = WS(
        'published', 'Published',
        'Available for a Professional self assign.'
    )

    assigned = WS(
        'assigned', 'Assigned',
        'Assignment assigned and waiting for scheduling.'
    )

    scheduled = WS(
        'scheduled', 'Scheduled',
        'Assignment scheduled.'
    )

    cancelled = WS(
        'cancelled', 'Cancelled',
        'Assignment was cancelled by the customer.'
    )

    awaiting_assets = WS(
        'awaiting_assets', 'Awaiting Uploads',
        'Waiting for content to be upload to the system.'
    )

    in_qa = WS(
        'in_qa', 'Quality assurance',
        'Assignment is under quality assurance.'
    )

    approved = WS(
        'approved', 'Content approved',
        'Content was approved by Briefy quality assurance team'
    )

    refused = WS(
        'refused', 'Customer refused',
        'Assignment was rejected by the customer.'
    )

    completed = WS(
        'completed', 'Completed',
        'Assignment is completed.'
    )

    # Transitions
    @created.transition(validation, 'can_submit')
    @edit.transition(validation, 'can_submit')
    def submit(self):
        """After Assignment creation, or edition submit it to machine validation."""
        pass

    @validation.transition(pending, 'can_validate')
    def validate(self):
        """Validate an Assignment."""
        pass

    @validation.transition(edit, 'can_validate')
    def invalidate(self):
        """Invalidate an Assignment, sending it to edit."""
        pass

    @pending.transition(assigned, 'can_assign')
    def assign(self):
        """Assign an Assignment to a professional."""
        pass

    @pending.transition(published, 'can_publish')
    def publish(self):
        """Put the Assignment to be self assigned."""
        pass

    @published.transition(pending, 'can_retract')
    def retract(self):
        """Remove a Assignment from the Pool."""
        pass

    @published.transition(assigned, 'can_self_assign')
    def self_assign(self):
        """Professional gets an Assignment."""
        pass

    @assigned.transition(scheduled, 'can_schedule')
    @awaiting_assets.transition(scheduled, 'can_schedule')
    def schedule(self):
        """Professional schedules the Assignment."""
        pass

    @assigned.transition(assigned, 'can_schedule')
    def scheduling_issues(self):
        """Professional reports scheduling issues."""
        pass

    @scheduled.transition(awaiting_assets, 'can_get_ready_for_upload')
    def ready_for_upload(self):
        """System moves Assignment to awaiting for upload."""
        pass

    @awaiting_assets.transition(in_qa, 'can_upload')
    def upload(self):
        """Professional submits all assets for QA."""
        pass

    @in_qa.transition(pending, 'can_unassign')
    def unassign(self):
        """QA unassign an Assignment."""
        # Update state and comments on Knack
        pass

    @in_qa.transition(approved, 'can_approve')
    def approve(self):
        """QA approves an Assignment."""
        assignment = self.document
        if not assignment.approvable:
            raise self.state.exception_transition(
                'Incorrect number of assets.'
            )
        # Transition all pending assets to approved
        transitions.approve_assets_in_assignment(assignment, self.context)

    @in_qa.transition(awaiting_assets, 'can_approve', require_message=True)
    def reject(self):
        """QA rejects an Assignment."""
        pass

    @approved.transition(in_qa, 'can_retract_approval')
    @refused.transition(in_qa, 'can_retract_approval_customer')
    def retract_approval(self):
        """QA retracts the approval."""
        pass

    @approved.transition(completed, 'can_complete')
    @refused.transition(completed, 'can_complete_from_refused')
    def complete(self):
        """Customer approve the Assignment."""
        pass

    @approved.transition(refused, 'can_refuse', require_message=True)
    def refuse(self):
        """Customer refuses the Assignment."""
        pass

    @approved.transition(approved, 'can_deliver')
    def deliver(self):
        """Execute the delivery of assets from the Assignment."""
        pass

    @pending.transition(cancelled, 'can_cancel')
    @published.transition(cancelled, 'can_cancel')
    @assigned.transition(cancelled, 'can_cancel')
    @scheduled.transition(scheduled, 'can_cancel')
    def cancel(self):
        """Customer or Briefy cancel the Assignment."""
        pass

    @Permission(groups=[G['customers'], G['bizdev'], G['system']])
    def can_submit(self):
        """Validate if user can submit the Assignment."""
        return True

    @Permission(groups=[G['scout'], G['pm']])
    def can_assign(self):
        """Validate if user can assign the Assignment to a Professional."""
        return True

    @Permission(groups=[G['professionals'], ])
    def can_self_assign(self):
        """Validate if user is able to self assign this Assignment."""
        # TODO: Check for existing Assignments in the same date.
        return True

    @Permission(groups=[G['system'], ])
    def can_validate(self):
        """Validate if user is system."""
        return True

    @Permission(groups=[G['customers'], G['pm'], G['scout'], G['system']])
    def can_publish(self):
        """Validate if user can publish this Assignment."""
        return True

    @Permission(groups=[G['customers'], G['pm'], G['scout']])
    def can_retract(self):
        """Validate if user can retract an Assignment."""
        return True

    @Permission(groups=[G['professionals'], G['pm']])
    def can_schedule(self):
        """Validate if user can schedule an Assignment."""
        return True

    @Permission(groups=[G['system'], ])
    def can_get_ready_for_upload(self):
        """Validate if user can move an Assignment to waiting for assets."""
        return True

    @Permission(groups=[G['professionals'], G['qa'], ])
    def can_upload(self):
        """Validate if user can move an Assignment to qa."""
        return True

    @Permission(groups=[LR['qa_manager'], G['qa'], G['pm'], ])
    def can_unassign(self):
        """Validate if user can un assign an Assignment."""
        return True

    @Permission(groups=[LR['qa_manager'], G['qa'], ])
    def can_approve(self):
        """Validate if user can approve an Assignment."""
        return True

    @Permission(groups=[LR['qa_manager'], G['qa'], ])
    def can_reject(self):
        """Validate if user can reject an Assignment."""
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
        """Validate if user can move an Assignment to completed."""
        return True

    @Permission(groups=[G['customers'], G['pm']])
    def can_complete_from_refused(self):
        """Validate if user can move an Assignment to completed from refused state."""
        return True

    @Permission(groups=[G['customers'], ])
    def can_refuse(self):
        """Validate if user can reject an Assignment as a customer."""
        return True

    @Permission(groups=[G['customers'], ])
    def can_cancel(self):
        """Validate if user can cancel an Assignment as a customer."""
        return True

    @Permission(groups=[G['system'], ])
    def can_deliver(self):
        """Validate if user can execute a deliver transition."""
        return True


class OrderLocationWorkflow(BriefyWorkflow):
    """Workflow for a OrderLocation."""

    entity = 'orderlocation'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'OrderLocation inserted on the database.'
    )


class OrderWorkflow(BriefyWorkflow):
    """Workflow for a Order."""

    entity = 'order'
    initial_state = 'received'

    # States
    received = WS(
        'received', 'Received',
        'Order received to be executed.'
    )

    assigned = WS(
        'assigned', 'Assigned',
        'Order assigned to a Professional.'
    )

    scheduled = WS(
        'scheduled', 'Scheduled',
        'Order scheduled to be executed.'
    )

    in_qa = WS(
        'in_qa', 'In QA',
        'Order in the quality assurance validation.'
    )

    cancelled = WS(
        'cancelled', 'Cancelled',
        'Order cancelled.'
    )

    approved = WS(
        'approved', 'Approved',
        'Order approved by quality assurance.'
    )

    refused = WS(
        'refused', 'Refused',
        'Order refused.'

    )

    # Transitions
    @received.transition(assigned, 'can_assign')
    def assign(self):
        """Transition: Inform the assignment to the customer."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], G['scout'], ])
    def can_assign(self):
        """Permission: Validate if user can assign a Order.

        Groups: g:pm, g:scout, r:project_manager
        """
        return True

    @scheduled.transition(cancelled, 'can_cancel')
    @assigned.transition(cancelled, 'can_cancel')
    @received.transition(cancelled, 'can_cancel')
    def cancel(self):
        """Transition: Cancel the Order."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], G['customers'], G['finance']])
    def can_cancel(self):
        """Permission: Validate if user can move the Order to the cancelled state.

        Groups: g:pm, g:finance, g:customers, r:project_manager
        """
        # TODO: validate if the restrictions before cancel the Order
        return True

    @received.transition(scheduled, 'can_schedule')
    @assigned.transition(scheduled, 'can_schedule')
    def schedule(self):
        """Transition: Inform the schedule to the customer."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], G['scout'], ])
    def can_schedule(self):
        """Permission: Validate if user can schedule an Order.

        Groups: g:pm, g:scout, r:project_manager
        """
        return True

    @scheduled.transition(in_qa, 'can_start_qa')
    def start_qa(self):
        """Transition: Inform the start of QA to the customer."""
        pass

    @Permission(groups=[LR['project_manager'], LR['professional_user'], G['pm'], G['qa'], ])
    def can_start_qa(self):
        """Permission: Validate if user can move an Order into the in_qa state.

        Groups: g:pm, g:qa, r:project_manager, r:professional
        """
        return True

    @in_qa.transition(approved, 'can_approve')
    def approve(self):
        """Transition: Inform the approval of the Order to the customer."""
        pass

    @Permission(groups=[LR['qa_manager'], G['qa'], ])
    def can_approve(self):
        """Permission: Validate if user can approve the Order.

        Groups: g:qa, r:qa_manager
        """
        return True

    @approved.transition(refused, 'can_refuse')
    def refuse(self):
        """Transition: Customer refuse the Order."""
        pass

    # TODO: add LR pm_customer
    @Permission(groups=[G['pm']])
    def can_refuse(self):
        """Permission: Validate if user can refuse the Order.

        Groups: g:pm, r:pm_customer
        """
        return True

    @in_qa.transition(assigned, 'can_reassign')
    @refused.transition(assigned, 'can_reassign')
    def reassign(self):
        """Transition: Inform the re-assignment of the Order the customer."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], ])
    def can_reassign(self):
        """Permission: Validate if user reassign an Order.

        Groups: g:pm, r:project_manager
        """
        return True


class PoolWorkflow(BriefyWorkflow):
    """Workflow for a Pool."""

    entity = 'pool'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Pool created.'
    )

    active = WS(
        'active', 'Active',
        'Pool is active.'
    )

    inactive = WS(
        'inactive', 'Inactive',
        'Pool is inactive.'
    )

    @created.transition(active, 'submit')
    def submit(self):
        """Transition: Pool was submitted."""
        pass

    @Permission(groups=[G['scout'], G['pm'], ])
    def can_submit(self):
        """Permission: Validate if user can submit a Pool.

        Groups: g:pm, g:scout
        """
        return True

    @active.transition(inactive, 'can_disable')
    def disable(self):
        """Transition: Pool was moved to inactive."""
        pass

    @Permission(groups=[G['scout'], G['pm'], ])
    def can_disable(self):
        """Permission: Validate if user can inactive a Pool.

        Groups: g:pm, g:scout
        """
        return True

    @inactive.transition(active, 'can_reactivated')
    def reactivated(self):
        """Transition: Pool was moved back to active."""
        pass

    @Permission(groups=[G['scout'], G['pm'], ])
    def can_reactivated(self):
        """Permission: Validate if user can reactivated a Pool.

        Groups: g:pm, g:scout
        """
        return True
