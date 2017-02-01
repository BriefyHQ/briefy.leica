"""Order, OrderLocation, Assignment and Pool related workflow."""
from briefy.common.db import datetime_utcnow
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.vocabularies.roles import LocalRolesChoices as LR
from briefy.common.users import SystemUser
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import WorkflowTransitionException
from briefy.leica.subscribers.utils import create_new_assignment_from_order

import logging


logger = logging.getLogger(__name__)


SHOOT_TIME_FUTURE_MSG = 'Shoot time should be at least one day in the future.'
ASSIGN_AFTER_RENEWSHOOT = 'Creative automatically assigned due to a reshoot.'


class AssignmentWorkflow(BriefyWorkflow):
    """Workflow for a Assignment."""

    entity = 'assignment'
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
        'published', 'Pool',
        'Available for Professional self assignment.'
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
        'Content was approved by Briefy quality assurance team.'
    )

    refused = WS(
        'refused', 'Customer refused',
        'Assignment was rejected by the customer.'
    )

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
    def submit(self, **kwargs):
        """Submit Assignment."""
        # Assignment creation handled by Order creation event subscriber
        pass

    @Permission(groups=[G['customers'], G['pm'], G['bizdev'], G['system'], ])
    def can_submit(self):
        """Validate if user can submit an Assignment."""
        return True

    @pending.transition(
        assigned,
        'can_assign',
        required_fields=('professional_id',)
    )
    def assign(self, **kwargs):
        """Define a Professional to the Assignment."""
        fields = kwargs['fields']
        assignment = self.document
        order = assignment.order
        if order.state == 'received':
            order.workflow.assign()
        # set local role
        professional_id = fields.get('professional_id')
        if professional_id:
            assignment.professional_user = professional_id

    @Permission(groups=[G['scout'], G['pm'], ])
    def can_assign(self):
        """Validate if user can set the Professional in the Assignment."""
        return True

    @pending.transition(
        published, 'can_publish',
        required_fields=('pool_id', ),
    )
    def publish(self, **kwargs):
        """Inform availability dates and move the enable Assignment to be self assigned."""
        order = self.document.order
        if not order.availability:
            return False
        else:
            return True

    @Permission(groups=[G['customers'], G['pm'], G['scout'], G['system'], ])
    def can_publish(self):
        """Validate if user can publish this Assignment."""
        return True

    @published.transition(pending, 'can_retract')
    def retract(self, **kwargs):
        """Remove availability dates and return Assignment to pending."""
        order = self.document.order
        order.availability = []

    @Permission(groups=[G['customers'], G['pm'], G['scout'], ])
    def can_retract(self):
        """Validate if user can retract the Assignment from Pool."""
        return True

    @published.transition(
        assigned,
        'can_self_assign',
        required_fields=('scheduled_datetime', 'professional_id')
    )
    def self_assign(self, **kwargs):
        """Professional choose the Assignment from the Pool."""
        # workflow event subscriber will move to schedule after
        assignment = self.document
        order = assignment.order
        if order.state == 'received':
            order.workflow.context = SystemUser
            order.workflow.assign()
        # set local role
        professional_id = self.context.id
        assignment.professional_user = professional_id

    @Permission(groups=[G['professionals'], G['pm'], G['scout'], G['system']])
    def can_self_assign(self):
        """Validate if user is able to self assign this Assignment."""
        # TODO: Check for existing Assignment already schedule to the same date.
        return True

    @assigned.transition(
        scheduled,
        'can_schedule',
        required_fields=('scheduled_datetime', )
    )
    def schedule(self, **kwargs):
        """Professional, Scout or PM schedule the Assignment."""
        fields = kwargs.get('fields')
        now = datetime_utcnow()
        date_diff = fields.get('scheduled_datetime') - now
        if date_diff.days < 1:
            msg = SHOOT_TIME_FUTURE_MSG
            raise WorkflowTransitionException(msg)
        else:
            order = self.document.order
            if order.state == 'assigned':
                order.workflow.context = SystemUser
                order.workflow.schedule()

    @Permission(groups=[G['professionals'], G['pm'], G['scout'], G['system']])
    def can_schedule(self):
        """Validate if user can schedule an Assignment."""
        return True

    @awaiting_assets.transition(
        scheduled,
        'can_reschedule',
        required_fields=('scheduled_datetime', )
    )
    @scheduled.transition(
        scheduled,
        'can_reschedule',
        required_fields=('scheduled_datetime', )
    )
    def reschedule(self, **kwargs):
        """Professional or PM reschedule an Assignment."""
        fields = kwargs.get('fields')
        now = datetime_utcnow()
        date_diff = fields.get('scheduled_datetime') - now
        if date_diff.days < 1:
            msg = SHOOT_TIME_FUTURE_MSG
            raise WorkflowTransitionException(msg)

    @assigned.transition(
        assigned,
        'can_reschedule',
        require_message=True,
    )
    def scheduling_issues(self, **kwargs):
        """Professional or PM reports scheduling issues."""
        # subscriber will create a new Comment instance from this transition
        pass

    @Permission(groups=[G['professionals'], G['pm']])
    def can_reschedule(self):
        """Validate if user can reschedule an Assignment."""
        return True

    @scheduled.transition(assigned, 'can_remove_schedule')
    def remove_schedule(self, **kwargs):
        """Customer, Professional or PM removes the Assignment scheduled shoot datetime."""
        pass

    @Permission(groups=[G['professionals'], G['customers'], G['pm']])
    def can_remove_reschedule(self):
        """Validate if user can remove schedule shoot date time of an Assignment."""
        return True

    @pending.transition(cancelled, 'can_cancel')
    @published.transition(cancelled, 'can_cancel')
    @assigned.transition(cancelled, 'can_cancel')
    @scheduled.transition(cancelled, 'can_cancel')
    @awaiting_assets.transition(cancelled, 'can_cancel')
    def cancel(self, **kwargs):
        """Customer or PM cancel the Assignment."""
        now = datetime_utcnow()
        assignment = self.document
        allowed = False
        scheduled_datetime = assignment.scheduled_datetime
        if self.state == self.scheduled:
            date_diff = scheduled_datetime - now
            if date_diff.days >= 1:
                allowed = True
        elif self.state == self.awaiting_assets:
            submission_path = assignment.submission_path
            date_diff = now - scheduled_datetime
            # let cancel if the there is no upload after 4 days
            if not submission_path and date_diff.days >= 4:
                allowed = True
        return allowed

    @Permission(groups=[G['customers'], G['pm'], G['qa'], ])
    def can_cancel(self):
        """Validate if user can cancel an Assignment."""
        return True

    @scheduled.transition(awaiting_assets, 'can_get_ready_for_upload')
    def ready_for_upload(self, **kwargs):
        """System moves Assignment to awaiting assets (upload)."""
        now = datetime_utcnow()
        assignment = self.document
        scheduled_datetime = assignment.scheduled_datetime
        date_diff = scheduled_datetime - now
        if date_diff.total_seconds() >= 0:
            return True
        else:
            return False

    @Permission(groups=[G['system'], ])
    def can_get_ready_for_upload(self):
        """Validate if user can move an Assignment from scheduled to waiting for assets."""
        return True

    @awaiting_assets.transition(in_qa, 'can_approve')
    def retract_rejection(self, **kwargs):
        """QA retract rejection or manually move to QA."""
        assignment = self.document
        last_revision = assignment.versions[-1]
        assignment.set_type = last_revision.set_type
        return True

    @in_qa.transition(
        approved,
        'can_approve',
        required_fields=('qa_manager', )
    )
    def approve(self, **kwargs):
        """QA approves the Assignment Set."""
        # TODO: return this validation when Mr.C is back
        # assignment = self.document
        # if not assignment.approvable:
        #     raise self.state.exception_transition(
        #         'Incorrect number of assets.'
        #     )
        # # Transition all pending assets to approved
        # transitions.approve_assets_in_assignment(assignment, self.context)

        # This will not trigger the Order just the event to start ms.laure.
        pass

    @in_qa.transition(
        awaiting_assets, 'can_approve',
        require_message=True,
        required_fields=('qa_manager', )
    )
    def reject(self, **kwargs):
        """QA rejects Assignment Set."""
        assignment = self.document
        assignment.set_type = 'returned_photographer'
        return True

    @in_qa.transition(perm_rejected, 'can_approve')
    def perm_reject(self, **kwargs):
        """QA permanently reject the Assignment Set."""
        order = self.document.order
        if order.state == 'in_qa':
            order.workflow.new_shoot()

    @approved.transition(in_qa, 'can_approve')
    def retract_approval(self, **kwargs):
        """QA retracts the approval."""
        # TODO: should we move the Order back if delivered?
        pass

    @Permission(groups=[LR['qa_manager'], G['qa'], ])
    def can_approve(self):
        """Validate if user can approve or reject an Assignment Set."""
        return True

    @awaiting_assets.transition(
        asset_validation,
        'can_upload',
        required_fields=('submission_path', )
    )
    def upload(self, **kwargs):
        """Professional submits all assets for QA."""
        pass

    @Permission(groups=[G['professionals'], G['qa'], G['pm'], ])
    def can_upload(self):
        """Validate if user can update submission link and move an Assignment to QA."""
        return True

    @asset_validation.transition(
        in_qa,
        'can_validate_assets',
        require_message=True,
    )
    def validate_assets(self, **kwargs):
        """System validate uploaded Assets."""
        order = self.document.order
        if order.state == 'scheduled':
            message = kwargs.get('message')
            order.workflow.context = self.context
            order.workflow.start_qa(message=message)

    @asset_validation.transition(
        awaiting_assets,
        'can_validate_assets',
        require_message=True,
    )
    def invalidate_assets(self, **kwargs):
        """System invalidate uploaded Assets."""
        pass

    @Permission(groups=[G['system'], G['qa']])
    def can_validate_assets(self):
        """Validate if the user can automatic validate /invalidate Assets from an Assignment Set."""
        return True

    @refused.transition(in_qa, 'can_return_to_qa')
    def return_to_qa(self, **kwargs):
        """PM move Assignment back to QA for further revision."""
        assignment = self.document
        message = kwargs.get('message', '')
        assignment.set_type = 'refused_customer'
        order = assignment.order
        if order.state == 'refused':
            order.workflow.require_revision(message=message)
        return True

    @Permission(groups=[G['pm'], ])
    def can_return_to_qa(self):
        """Validate if the user can return to QA (futher revision) an Assignment Set."""
        return True

    @in_qa.transition(completed, 'can_complete')
    @approved.transition(completed, 'can_complete')
    @refused.transition(completed, 'can_complete')
    def complete(self, **kwargs):
        """Customer, System or PM accept the Assignment Set."""
        # this should be only executed only from the order
        pass

    @Permission(groups=[G['customers'], G['pm'], G['system']])
    def can_complete(self):
        """Validate if user can move an Assignment to completed."""
        return True

    @approved.transition(refused, 'can_refuse', require_message=True)
    def refuse(self, **kwargs):
        """Customer or PM refuses the Assignment Set."""
        # this should be only executed only from the order
        pass

    @Permission(groups=[G['customers'], G['pm'], ])
    def can_refuse(self):
        """Validate if user can refuse an Assignment Set."""
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
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Order created.'
    )

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

    delivered = WS(
        'delivered', 'Delivered',
        'Order delivered by quality assurance.'
    )

    accepted = WS(
        'accepted', 'Accepted',
        'Order accepted by the customer.'
    )

    refused = WS(
        'refused', 'Refused',
        'Order refused by the customer.'
    )

    perm_refused = WS(
        'perm_refused', 'Permanently Refused',
        'Order permanently refused.'
    )

    # Transitions
    @created.transition(received, 'can_submit')
    def submit(self, **kwargs):
        """Submit Order."""
        # OrderCreatedEvent subscriber will handle the Assignment creation
        pass

    @Permission(groups=[G['customers'], G['pm'], G['bizdev'], G['system'], ])
    def can_submit(self):
        """Validate if user can submit an Order."""
        return True

    @received.transition(assigned, 'can_assign')
    def assign(self, **kwargs):
        """Transition: Assign a Professional to an Order."""
        # should be only used by the Assignment workflow
        return True

    @Permission(groups=[LR['project_manager'], G['pm'], G['scout'], G['system'], ])
    def can_assign(self):
        """Permission: Validate if user can assign a Order.

        Groups: g:pm, g:scout, r:project_manager
        """
        return True

    @assigned.transition(received, 'can_unassign')
    @scheduled.transition(received, 'can_unassign')
    def unassign(self, **kwargs):
        """Transition: Un-assign the Order by cancel the Assignment and create a new one."""
        order = self.document
        message = kwargs.get('message', '')
        order.assignment.workflow.cancel(message=message)
        create_new_assignment_from_order(order, order.request)
        return True

    @Permission(groups=[LR['project_manager'], G['pm'], ])
    def can_unassign(self):
        """Permission: Validate if user can unassign an Order.

        Groups: g:pm, r:project_manager
        """
        return True

    @assigned.transition(received, 'can_remove_availability')
    @scheduled.transition(received, 'can_remove_availability')
    def remove_availability(self, **kwargs):
        """Transition: Inform the removal of availability dates to the customer."""
        order = self.document
        order.availability = []
        # this will handle the creation of a new Assignment
        message = kwargs.get('message', '')
        order.assignment.workflow.cancel(message=message)
        return True

    @Permission(groups=[LR['project_manager'], G['pm'], LR['customer_user'], G['customers'], ])
    def can_remove_availability(self):
        """Permission: Validate if user can remove availability dates of an Order.

        Groups: g:pm, r:project_manager, g:customers, r:customer_user
        """
        # TODO: make sure customer only unassign
        return True

    @assigned.transition(
        assigned, 'can_reassign',
        required_fields=('professional_id', )
    )
    @scheduled.transition(
        assigned, 'can_reassign',
        required_fields=('professional_id', )
    )
    def reassign(self, **kwargs):
        """Transition: Inform the reassignment to the customer."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], ])
    def can_reassign(self):
        """Permission: Validate if user can reassign an Order.

        Groups: g:pm, r:project_manager
        """
        return True

    @scheduled.transition(assigned, 'can_remove_schedule')
    def remove_schedule(self, **kwargs):
        """Transition: Inform the removal of the schedule shoot datetime to the customer."""
        pass

    @Permission(groups=[LR['project_manager'], G['pm'], G['professionals'], G['customers'], ])
    def can_remove_schedule(self):
        """Permission: Validate if user can remove the schedule of an Order.

        Groups: g:pm, r:project_manager
        """
        return True

    @scheduled.transition(cancelled, 'can_cancel', message_required=True)
    @assigned.transition(cancelled, 'can_cancel', message_required=True)
    @received.transition(cancelled, 'can_cancel', message_required=True)
    def cancel(self, **kwargs):
        """Transition: Cancel the Order."""
        order = self.document
        assignment = order.assignment
        wkf = assignment.workflow
        wkf.context = self.context
        assignment.workflow.cancel()

    @Permission(groups=[LR['project_manager'], LR['customer_user'], G['pm'], G['customers'], ])
    def can_cancel(self):
        """Permission: Validate if user can move the Order to the cancelled state.

        Groups: g:pm, g:customers, r:project_manager, r:customer_user
        """
        # TODO: validate if the restrictions before cancel the Order
        return True

    @received.transition(scheduled, 'can_schedule')
    @assigned.transition(scheduled, 'can_schedule')
    def schedule(self, **kwargs):
        """Transition: Inform the schedule to the customer."""
        # this should be executed from the assignment
        pass

    @Permission(groups=[LR['project_manager'], LR['professional_user'],
                        G['pm'], G['scout'], G['system'], ])
    def can_schedule(self):
        """Permission: Validate if user can schedule an Order.

        Groups: g:pm, g:scout, r:project_manager, r:professional_user
        """
        return True

    @scheduled.transition(in_qa, 'can_start_qa')
    def start_qa(self, **kwargs):
        """Transition: Inform the start of QA to the customer."""
        # this should be executed from the assignment
        pass

    @Permission(groups=[G['system'], G['qa'], ])
    def can_start_qa(self):
        """Permission: Validate if user can move an Order into the in_qa state.

        Groups: g:system, g:qa
        """
        return True

    @in_qa.transition(
        delivered, 'can_deliver',
        required_fields=('delivery', )
    )
    def deliver(self, **kwargs):
        """Transition: Inform the deliver of the Order to the customer."""
        pass

    @Permission(groups=[LR['qa_manager'], G['qa'], G['system'], ])
    def can_deliver(self):
        """Permission: Validate if user can deliver the Order.

        Groups: g:qa, g:system, r:qa_manager
        """
        return True

    @delivered.transition(refused, 'can_refuse', message_required=True)
    def refuse(self, **kwargs):
        """Transition: Customer refuse the Order."""
        # TODO: fix workflow to pass message in the kwargs
        message = kwargs.get('message')
        order = self.document
        assignment = order.assignment
        assignment.workflow.refuse(message=message)

    @Permission(groups=[G['pm'], G['customers'], LR['project_manager'], LR['customer_user'], ])
    def can_refuse(self):
        """Permission: Validate if user can refuse an Order.

        Groups: g:pm, g:customers, r:customer_user, r:project_manager
        """
        return True

    @in_qa.transition(assigned, 'can_reshoot')
    @refused.transition(assigned, 'can_reshoot')
    def reshoot(self, **kwargs):
        """Transition: Inform the reshoot of the Order the customer."""
        message = kwargs.get('message', '')
        order = self.document
        order.availability = []
        old_assignment = order.assignment
        old_assignment.workflow.complete(message=message)
        new_assignment = create_new_assignment_from_order(order, order.request)
        professional_id = old_assignment.professional_id
        fields = dict(professional_id=professional_id)
        message = ASSIGN_AFTER_RENEWSHOOT
        new_assignment.workflow.assign(fields=fields, message=message)

    @Permission(groups=[LR['project_manager'], G['pm'], G['qa'], ])
    def can_reshoot(self):
        """Permission: Validate if user can reshoot an Order.

        Groups: g:pm, r:project_manager
        """
        return True

    @in_qa.transition(received, 'can_new_shoot')
    @refused.transition(received, 'can_new_shoot')
    def new_shoot(self, **kwargs):
        """Transition: Inform the new shoot of an Order the customer."""
        message = kwargs.get('message', '')
        order = self.document
        order.availability = []
        old_assignment = order.assignment
        old_assignment.workflow.complete(message=message)
        create_new_assignment_from_order(order, order.request)

    @Permission(groups=[LR['project_manager'], G['pm'], G['qa'], ])
    def can_new_shoot(self):
        """Permission: Validate if user can reshoot an Order.

        Groups: g:pm, g:customers, r:project_manager, r:customer_user
        """
        return True

    @delivered.transition(accepted, 'can_accept')
    @refused.transition(accepted, 'can_accept')
    def accept(self, **kwargs):
        """Transition: Customer or PM accept an Order."""
        order = self.document
        final_states = ('cancelled', 'perm_rejected', 'completed')
        for assignment in order.assignments:
            if assignment.state == 'approved':
                assignment.workflow.complete()
            elif assignment.state not in final_states:
                return False

    @Permission(
        groups=[G['pm'], G['customers'], G['system'], LR['project_manager'], LR['customer_user'], ]
    )
    def can_accept(self):
        """Permission: Validate if user can accept an Order.

        Groups: g:pm, g:customers, g:system, r:customer_user, r:project_manager
        """
        return True

    @refused.transition(perm_refused, 'can_perm_refuse', message_required=True)
    def perm_refuse(self, **kwargs):
        """Transition: PM permanently refuse an Order."""
        pass

    @Permission(groups=[G['pm'], G['bizdev'], LR['project_manager']])
    def can_perm_refuse(self):
        """Permission: Validate if user can permanently refuse an Order.

        Groups: g:pm, g:bizdev, r:project_manager
        """
        return True

    @refused.transition(in_qa, 'can_require_revision')
    def require_revision(self, **kwargs):
        """Transition: PM or Customer require revision of an Order."""
        # this should be triggered from the Assignment
        pass

    @Permission(groups=[G['pm'], ])
    def can_require_revision(self):
        """Permission: Validate if user can require revision of an Order."""
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
    def submit(self, **kwargs):
        """Transition: Pool was submitted."""
        pass

    @Permission(groups=[G['scout'], G['pm'], ])
    def can_submit(self):
        """Permission: Validate if user can submit a Pool.

        Groups: g:pm, g:scout
        """
        return True

    @active.transition(inactive, 'can_disable')
    def disable(self, **kwargs):
        """Transition: Pool was moved to inactive."""
        pass

    @Permission(groups=[G['scout'], G['pm'], ])
    def can_disable(self):
        """Permission: Validate if user can inactive a Pool.

        Groups: g:pm, g:scout
        """
        return True

    @inactive.transition(active, 'can_reactivated')
    def reactivated(self, **kwargs):
        """Transition: Pool was moved back to active."""
        pass

    @Permission(groups=[G['scout'], G['pm'], ])
    def can_reactivated(self):
        """Permission: Validate if user can reactivated a Pool.

        Groups: g:pm, g:scout
        """
        return True
