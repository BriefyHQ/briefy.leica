"""Assignment workflow."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.vocabularies.roles import LocalRolesChoices as LR
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowTransitionException
from briefy.leica.config import SCHEDULE_DAYS_LIMIT
from briefy.leica.events.assignment import AssignmentUpdatedEvent
from briefy.leica.utils.transitions import create_comment_on_assignment_approval


SELF_ASSIGN_SCOUT_ID = 'f1233fb7-c482-454f-a12d-8f9305755774'

SHOOT_TIME_FUTURE_MSG = 'Shoot time should be at least one day in the future.'

# required fields
PAYOUT_REQUIRED_FIELDS = ('payout_value', 'payout_currency', 'travel_expenses')
COMPENSATION_REQUIRED_FIELDS = ('additional_compensation', 'reason_additional_compensation')
ASSIGN_REQUIRED_FIELDS = (
    'payout_value',
    'payout_currency',
    'travel_expenses',
    'professional_id'
)
PERM_REJECT_REQUIRED_FIELDS = (
    'additional_compensation',
    'reason_additional_compensation'
)


class AssignmentWorkflow(BriefyWorkflow):
    """Workflow for a Assignment."""

    entity = 'assignment'
    initial_state = 'created'
    update_event = AssignmentUpdatedEvent

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

    post_processing = WS(
        'post_processing', 'Post Processing',
        'Assignment is in post processing.'
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

    @Permission(groups=[G['customers'], G['pm'], G['qa'], G['bizdev'], G['system'], ])
    def can_submit(self):
        """Validate if user can submit an Assignment."""
        return True

    @pending.transition(
        assigned,
        'can_assign',
        required_fields=ASSIGN_REQUIRED_FIELDS
    )
    def assign(self, **kwargs):
        """Define a Professional to the Assignment."""
        user_id = str(self.context.id)
        assignment = self.document
        order = assignment.order
        if order.state == 'received':
            fields = {'scout_manager': user_id}
            order.workflow.assign(fields=fields)
        # set local roles
        fields = kwargs['fields']
        assignment.scout_manager = user_id
        professional_id = fields.get('professional_id')
        assignment.professional_user = professional_id
        # force explicit here but it will also be set by the workflow engine
        assignment.professional_id = professional_id

    @Permission(groups=[G['scout'], G['pm'], G['qa'], G['system'], ])
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
            fields = {
                'scout_manager': SELF_ASSIGN_SCOUT_ID
            }
            order.workflow.assign(fields=fields)
        # set local roles
        assignment.scout_manager = SELF_ASSIGN_SCOUT_ID
        professional_id = self.context.id
        assignment.professional_user = professional_id
        # force here but this will also set by the workflow engine
        assignment.professional_id = professional_id

    @Permission(groups=[G['professionals'], G['system']])
    def can_self_assign(self):
        """Validate if user is able to self assign this Assignment."""
        # TODO: Check for existing Assignment already schedule to the same date.
        return True

    @published.transition(
        assigned,
        'can_assign_pool',
        required_fields=('scheduled_datetime', 'professional_id')
    )
    def assign_pool(self, **kwargs):
        """PM or Scout assign an Assignment from the Pool."""
        # workflow event subscriber will move to schedule after
        assignment = self.document
        order = assignment.order
        user_id = str(self.context.id)
        if order.state == 'received':
            fields = {
                'scout_manager': user_id
            }
            order.workflow.assign(fields=fields)
        # set local role
        assignment.scout_manager = user_id
        fields = kwargs['fields']
        professional_id = fields.get('professional_id')
        assignment.professional_user = professional_id

    @Permission(groups=[G['pm'], G['scout'], G['system']])
    def can_assign_pool(self):
        """Validate if user is able to assign this Assignment from Pool."""
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
        is_internal = 'g:briefy' in self.context.groups
        date_diff = fields.get('scheduled_datetime') - now
        if date_diff.days < int(SCHEDULE_DAYS_LIMIT) and not is_internal:
            msg = SHOOT_TIME_FUTURE_MSG
            raise WorkflowTransitionException(msg)

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
        is_internal = 'g:briefy' in self.context.groups
        scheduled_datetime = fields.get('scheduled_datetime')
        date_diff = scheduled_datetime - now
        if date_diff.days < int(SCHEDULE_DAYS_LIMIT) and not is_internal:
            msg = SHOOT_TIME_FUTURE_MSG
            raise WorkflowTransitionException(msg)

        # force update in the transition
        assignment = self.document
        order = assignment.order
        order.scheduled_datetime = scheduled_datetime

    @assigned.transition(
        assigned,
        'can_reschedule',
        require_message=True,
        required_fields=('additional_message',)
    )
    def scheduling_issues(self, **kwargs):
        """Professional or PM reports scheduling issues."""
        fields = kwargs.get('fields')
        additional_message = fields.get('additional_message').strip()
        if additional_message:
            kwargs['message'] += '\n\n{0}'.format(additional_message)
        return kwargs

    @Permission(groups=[G['professionals'], G['pm']])
    def can_reschedule(self):
        """Validate if user can reschedule an Assignment."""
        return True

    @scheduled.transition(assigned, 'can_remove_schedule')
    @awaiting_assets.transition(assigned, 'can_remove_schedule')
    def remove_schedule(self, **kwargs):
        """Customer, Professional or PM removes the Assignment scheduled shoot datetime."""
        assignment = self.document
        if assignment.submission_path:
            return False
        assignment.scheduled_datetime = None
        order = assignment.order
        order.scheduled_datetime = None

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
        assignment = self.document
        assignment.payout_value = 0
        assignment.scheduled_datetime = None
        order = assignment.order
        order.scheduled_datetime = None

    @Permission(groups=[G['customers'], G['pm'], G['system'], ])
    def can_cancel(self):
        """Validate if user can cancel an Assignment."""
        assignment = self.document
        user = self.context
        allowed = True
        uploaded = True if assignment.submission_path else False

        if G['customers'].value in user.groups:
            now = datetime_utcnow()
            scheduled_datetime = assignment.scheduled_datetime
            if scheduled_datetime:
                date_diff = scheduled_datetime - now
                if date_diff.days <= 1:
                    allowed = False

        return allowed and not uploaded

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

    @awaiting_assets.transition(
        in_qa,
        'can_retract_rejection',
        required_fields=('submission_path', )
    )
    def retract_rejection(self, **kwargs):
        """QA retract rejection or manually move to QA."""
        assignment = self.document
        last_revision = assignment.versions[-1]
        assignment.set_type = last_revision.set_type
        order = assignment.order
        if order.state == 'scheduled':
            message = kwargs.get('message')
            order.workflow.context = self.context
            order.workflow.start_qa(message=message)
        return True

    @Permission(groups=[G['qa'], G['pm'], G['system'], ])
    def can_retract_rejection(self):
        """Validate if user can retract the rejection of an Assignment Set."""
        return True

    @in_qa.transition(
        in_qa,
        'can_approve',
        require_message=True,
        required_fields=('qa_manager', )
    )
    def assign_qa_manager(self, **kwargs):
        """Set a QA manager for this assignment."""
        return True

    @in_qa.transition(
        approved,
        'can_approve',
        required_fields=('customer_message',)
    )
    @post_processing.transition(
        approved,
        'can_approve',
        required_fields=('customer_message',)
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

        # TODO: Copying assets to destination delivery and archive locations
        # is not instant.  Maybe we could have a transitory state
        # somewhat along "delivering_process" before "approved"

        if self.state == self.post_processing:
            assignment = self.document
            order = assignment.order
            # TODO: change this to use new configuration when available
            delivery = order.delivery
            if not delivery or not delivery.get('archive', None):
                raise WorkflowTransitionException('Can not approve without Archive URL.')

        customer_message = kwargs['fields'].get('customer_message', '').strip()
        if customer_message:
            actor = self.context.id
            assignment = self.document
            create_comment_on_assignment_approval(assignment, actor, customer_message)

    @in_qa.transition(
        awaiting_assets, 'can_approve',
        require_message=True,
    )
    def reject(self, **kwargs):
        """QA rejects Assignment Set."""
        assignment = self.document
        assignment.set_type = 'returned_photographer'
        return True

    @in_qa.transition(
        post_processing,
        'can_start_post_process',
    )
    def start_post_process(self, **kwargs):
        """QA start post processing the Assignment Set."""
        return True

    @Permission(groups=[G['qa'], G['system'], ])
    def can_start_post_process(self):
        """Validate if user can start post processing an Assignment Set."""
        return True

    @post_processing.transition(
        in_qa,
        'can_retract_post_process',
    )
    def retract_post_process(self, **kwargs):
        """QA retract post processing the Assignment Set."""
        return True

    @Permission(groups=[G['qa'], G['system'], ])
    def can_retract_post_process(self):
        """Validate if user can retract post processing an Assignment Set."""
        return True

    @in_qa.transition(
        perm_rejected,
        'can_perm_reject',
        required_fields=PERM_REJECT_REQUIRED_FIELDS
    )
    def perm_reject(self, **kwargs):
        """QA permanently reject the Assignment Set."""
        assignment = self.document
        assignment.payout_value = 0
        assignment.travel_expenses = 0
        return True

    @Permission(groups=[G['qa'], G['pm'], G['system'], ])
    def can_perm_reject(self):
        """Validate if user can perm_reject an Assignment Set."""
        return True

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

    @Permission(groups=[G['customers'], G['pm'], G['qa'], G['finance'], G['system']])
    def can_complete(self):
        """Validate if user can move an Assignment to completed."""
        return True

    @approved.transition(refused, 'can_refuse', require_message=True)
    def refuse(self, **kwargs):
        """Customer or PM refuses the Assignment Set."""
        # this should be only executed only from the order
        pass

    @Permission(groups=[G['customers'], G['pm'], G['system'], ])
    def can_refuse(self):
        """Validate if user can refuse an Assignment Set."""
        return True

    @pending.transition(pending, 'can_edit_payout', required_fields=PAYOUT_REQUIRED_FIELDS)
    @published.transition(published, 'can_edit_payout', required_fields=PAYOUT_REQUIRED_FIELDS)
    @assigned.transition(assigned, 'can_edit_payout', required_fields=PAYOUT_REQUIRED_FIELDS)
    @scheduled.transition(scheduled, 'can_edit_payout', required_fields=PAYOUT_REQUIRED_FIELDS)
    @awaiting_assets.transition(
        awaiting_assets, 'can_edit_payout', required_fields=PAYOUT_REQUIRED_FIELDS
    )
    @cancelled.transition(cancelled, 'can_edit_payout', required_fields=PAYOUT_REQUIRED_FIELDS)
    @in_qa.transition(in_qa, 'can_edit_payout', required_fields=PAYOUT_REQUIRED_FIELDS)
    @perm_rejected.transition(
        perm_rejected, 'can_edit_payout', required_fields=PAYOUT_REQUIRED_FIELDS
    )
    @approved.transition(approved, 'can_edit_payout', required_fields=PAYOUT_REQUIRED_FIELDS)
    @refused.transition(refused, 'can_edit_payout', required_fields=PAYOUT_REQUIRED_FIELDS)
    @completed.transition(completed, 'can_edit_payout', required_fields=PAYOUT_REQUIRED_FIELDS)
    def edit_payout(self, **kwargs):
        """Update payout and travel expenses of an Assignment."""
        pass

    @Permission(groups=[
        G['finance'], G['scout'], G['pm'], G['system'],
        G['product'], G['tech'], G['support']
    ])
    def can_edit_payout(self):
        """Validate if user can edit payout and travel expenses of an Assignment."""
        final_states = ('cancelled', 'completed', 'perm_rejected', )
        scout_states = ('pending', 'published',)
        user = self.context
        state = self.state
        support_groups = {G['product'], G['tech'], G['support']}
        is_support = support_groups.intersection(set(user.groups))
        has_permission = False

        if G['system'].value in user.groups:
            has_permission = True
        elif is_support:
            has_permission = True
        elif G['finance'].value in user.groups:
            has_permission = True
        elif G['scout'].value in user.groups and state.name not in scout_states:
            has_permission = False
        elif G['pm'].value in user.groups and state.name not in final_states:
            has_permission = True

        return has_permission

    @assigned.transition(
        assigned, 'can_edit_compensation', required_fields=COMPENSATION_REQUIRED_FIELDS
    )
    @scheduled.transition(
        scheduled, 'can_edit_compensation', required_fields=COMPENSATION_REQUIRED_FIELDS
    )
    @awaiting_assets.transition(
        awaiting_assets, 'can_edit_compensation', required_fields=COMPENSATION_REQUIRED_FIELDS
    )
    @cancelled.transition(
        cancelled, 'can_edit_compensation', required_fields=COMPENSATION_REQUIRED_FIELDS
    )
    @in_qa.transition(
        in_qa, 'can_edit_compensation', required_fields=COMPENSATION_REQUIRED_FIELDS
    )
    @perm_rejected.transition(
        perm_rejected, 'can_edit_compensation', required_fields=COMPENSATION_REQUIRED_FIELDS
    )
    @approved.transition(
        approved, 'can_edit_compensation', required_fields=COMPENSATION_REQUIRED_FIELDS
    )
    @refused.transition(
        refused, 'can_edit_compensation', required_fields=COMPENSATION_REQUIRED_FIELDS
    )
    @completed.transition(
        completed, 'can_edit_compensation', required_fields=COMPENSATION_REQUIRED_FIELDS
    )
    def edit_compensation(self, **kwargs):
        """Update additional compensation value and reason of an Assignment."""
        pass

    @Permission(groups=[
        G['finance'], G['pm'], G['system'],
        G['product'], G['tech'], G['support']
    ])
    def can_edit_compensation(self):
        """Validate if user can edit additional compensation value and reason of an Assignment."""
        final_states = ('cancelled', 'completed', 'perm_rejected', )
        user = self.context
        state = self.state
        support_groups = {G['product'], G['tech'], G['support']}
        is_support = support_groups.intersection(set(user.groups))
        has_permission = False

        if G['system'].value in user.groups:
            has_permission = True
        elif is_support or G['finance'].value in user.groups:
            has_permission = True
        elif G['pm'].value in user.groups and state.name not in final_states:
            has_permission = True

        return has_permission
