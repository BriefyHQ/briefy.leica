"""Base order workflow."""
from briefy.common.db import datetime_utcnow
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.vocabularies.roles import LocalRolesChoices as LR
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowTransitionException
from briefy.leica.events.order import OrderUpdatedEvent
from briefy.leica.subscribers.utils import create_new_assignment_from_order


ASSIGN_AFTER_RENEWSHOOT = 'Creative automatically assigned due to a re  shoot.'

# required fields
REQUIREMENTS_REQUIRED_FIELDS = ('number_required_assets', 'requirements', 'requirement_items')
ASSIGN_REQUIRED_FIELDS = (
    'payout_value',
    'payout_currency',
    'travel_expenses',
    'professional_id'
)
NEWSHOOT_REQUIRED_FIELDS = (
    'payout_value',
    'travel_expenses',
)
RESHOOT_REQUIRED_FIELDS = (
    'payout_value',
    'travel_expenses',
)
PERM_REJECT_REQUIRED_FIELDS = (
    'additional_compensation',
    'reason_additional_compensation'
)


class BaseOrderWorkflow(BriefyWorkflow):
    """Workflow for a Order."""

    entity = 'order'
    initial_state = 'created'
    update_event = OrderUpdatedEvent

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

    @received.transition(received, 'can_edit_location', required_fields=('location', ))
    @assigned.transition(assigned, 'can_edit_location', required_fields=('location', ))
    @scheduled.transition(scheduled, 'can_edit_location', required_fields=('location', ))
    def edit_location(self, **kwargs):
        """Update location in an Order."""
        order = self.document
        location = order.location
        if location:
            payload = kwargs['fields']['location']
            for key, value in payload.items():
                setattr(location, key, value)

            kwargs['fields'] = dict(location=location)

    @Permission(groups=[G['customers'], G['pm'], G['bizdev'], G['system'], ])
    def can_edit_location(self):
        """Validate if user can edit a location of an Order."""
        return True

    @received.transition(
        received,
        'can_edit_requirements',
        required_fields=REQUIREMENTS_REQUIRED_FIELDS
    )
    @assigned.transition(
        assigned,
        'can_edit_requirements',
        required_fields=REQUIREMENTS_REQUIRED_FIELDS)
    @scheduled.transition(
        scheduled,
        'can_edit_requirements',
        required_fields=REQUIREMENTS_REQUIRED_FIELDS)
    def edit_requirements(self, **kwargs):
        """Update requirements in an Order."""
        pass

    @Permission(groups=[G['customers'], G['pm'], G['bizdev'], G['system'], ])
    def can_edit_requirements(self):
        """Validate if user can edit requirements of an Order."""
        return True

    @received.transition(
        received,
        'can_set_availability',
        required_fields=('availability', )
    )
    @assigned.transition(
        assigned,
        'can_set_availability',
        required_fields=('availability', )
    )
    def set_availability(self, **kwargs):
        """Set order availability dates in the Order."""
        pass

    @Permission(groups=[G['customers'], G['pm'], G['bizdev'], G['system'], ])
    def can_set_availability(self):
        """Validate if user can set availability dates of an Order."""
        return True

    @received.transition(
        assigned,
        'can_assign',
    )
    def assign(self, **kwargs):
        """Transition: Assign a Professional to an Order."""
        # should be only used by the Assignment workflow
        return True

    @Permission(groups=[G['pm'], G['qa'], G['scout'], G['system'], ])
    def can_assign(self):
        """Permission: Validate if user can assign an Order.

        Groups: g:pm, g:scout, g:qa, g:system
        """
        return True

    @assigned.transition(received, 'can_unassign')
    @scheduled.transition(received, 'can_unassign')
    def unassign(self, **kwargs):
        """Transition: Un-assign the Order by cancel the Assignment and create a new one."""
        order = self.document
        old_assignment = order.assignments[-1]
        if not old_assignment.workflow.can_cancel:
            upload = True if old_assignment.submission_path else False
            if upload:
                msg = (
                    'It is not possible to unassign this order because the '
                    'assignment already have a submission.'
                )
            else:
                msg = (
                    'It is not possible to unassign this order because the '
                    'current assignment does not support a cancellation.'
                )
            raise WorkflowTransitionException(msg)
        message = kwargs.get('message', '')
        create_new_assignment_from_order(
            order,
            order.request,
            copy_payout=True,
            old_assignment=old_assignment
        )
        old_assignment.workflow.cancel(message=message)
        return True

    @Permission(groups=[G['pm'], G['system']])
    def can_unassign(self):
        """Permission: Validate if user can unassign an Order.

        Groups: g:pm, r:project_manager
        """
        return True

    @assigned.transition(received, 'can_remove_availability')
    @scheduled.transition(received, 'can_remove_availability')
    @received.transition(received, 'can_remove_availability')
    def remove_availability(self, **kwargs):
        """Transition: Inform the removal of availability dates to the customer."""
        order = self.document
        order.availability = []
        if order.state in ('assigned', 'scheduled'):
            old_assignment = order.assignments[-1]
            # this will handle the creation of a new Assignment
            message = kwargs.get('message', '')
            create_new_assignment_from_order(order, order.request, copy_payout=True)
            old_assignment.workflow.cancel(message=message)
        return True

    @Permission(groups=[G['pm'], G['customers'], G['support'], G['system']])
    def can_remove_availability(self):
        """Permission: Validate if user can remove availability dates of an Order.

        Groups: g:briefy_pm, r:project_manager, g:customers, g:briefy_support, r:customer_user
        """
        allowed = True
        order = self.document
        if order.state == 'received':
            user = self.context
            allowed = G['support'].value in user.groups
        return allowed

    @assigned.transition(
        assigned, 'can_reassign',
        required_fields=ASSIGN_REQUIRED_FIELDS
    )
    @scheduled.transition(
        assigned, 'can_reassign',
        required_fields=ASSIGN_REQUIRED_FIELDS
    )
    def reassign(self, **kwargs):
        """Transition: Inform the reassignment to the customer."""
        order = self.document
        user_id = str(self.context.id)
        order.scout_manager = user_id
        old_assignment = order.assignment
        message = kwargs.get('message', '')
        old_assignment.workflow.cancel(message=message)
        new_assignment = create_new_assignment_from_order(order, order.request)
        # pass message and fields to the assign transition of the Assignment
        new_assignment.workflow.assign(**kwargs)
        return True

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
        assignment = order.assignments[-1]
        wkf = assignment.workflow
        wkf.context = self.context
        assignment.workflow.cancel()

    @Permission(groups=[G['pm'], G['customers'], G['bizdev'], G['system'], ])
    def can_cancel(self):
        """Permission: Validate if user can move the Order to the cancelled state.

        Groups: g:pm, g:customers, r:project_manager, r:customer_user
        """
        order = self.document
        project = order.project
        assignment = order.assignments[-1] if order.assignments else None
        user = self.context
        allowed = True
        uploaded = False

        if assignment:
            uploaded = True if assignment.submission_path else False
            if G['customers'].value in user.groups:
                now = datetime_utcnow()
                scheduled_datetime = assignment.scheduled_datetime
                if scheduled_datetime:
                    date_diff = scheduled_datetime - now
                    if date_diff.days <= project.cancellation_window:
                        allowed = False

        return allowed and not uploaded

    @received.transition(
        scheduled,
        'can_schedule',
        required_fields=('scheduled_datetime', )
    )
    @assigned.transition(
        scheduled,
        'can_schedule',
        required_fields=('scheduled_datetime', )
    )
    def schedule(self, **kwargs):
        """Transition: Inform the schedule to the customer."""
        pass

    @Permission(groups=[G['pm'], G['scout'], G['system'], ])
    def can_schedule(self):
        """Permission: Validate if user can schedule an Order.

        Groups: g:pm, g:scout, g:system
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

    @Permission(groups=[G['qa'], G['system'], ])
    def can_deliver(self):
        """Permission: Validate if user can deliver the Order.

        Groups: g:qa, g:system
        """
        return True

    @delivered.transition(refused, 'can_refuse', message_required=True)
    def refuse(self, **kwargs):
        """Transition: Customer refuse the Order."""
        message = kwargs.get('message')
        order = self.document
        assignment = order.assignments[-1]
        assignment.workflow.refuse(message=message)

    @Permission(groups=[G['pm'], G['customers'], G['system'], ])
    def can_refuse(self):
        """Permission: Validate if user can refuse an Order.

        Groups: g:pm, g:customers, g:system
        """
        return True

    @in_qa.transition(
        assigned,
        'can_reshoot',
        required_fields=RESHOOT_REQUIRED_FIELDS
    )
    @refused.transition(
        assigned,
        'can_reshoot',
        required_fields=RESHOOT_REQUIRED_FIELDS
    )
    def reshoot(self, **kwargs):
        """Transition: Inform the reshoot of the Order the customer."""
        message = kwargs.get('message', '')
        order = self.document
        order.availability = []
        old_assignment = order.assignments[-1]
        # copy payout is not necessary in this case
        new_assignment = create_new_assignment_from_order(order, order.request)
        # prepare kwargs to assign the new assignment
        # explicit payout values are mandatory to assign transition
        # save original fields to use it to update old_assignment with posted values
        post_fields = kwargs['fields']
        kwargs.update(message=ASSIGN_AFTER_RENEWSHOOT)
        kwargs['fields'] = dict(
            professional_id=old_assignment.professional_id,
            payout_value=old_assignment.payout_value,
            payout_currency=old_assignment.payout_currency,
            travel_expenses=old_assignment.travel_expenses
        )
        # update old assignment and complete
        old_assignment.payout_value = post_fields.get('payout_value')
        old_assignment.travel_expenses = post_fields.get('travel_expenses')
        old_assignment.workflow.complete(message=message)
        # after complete the old assignment the new one can be assigned
        if new_assignment.state == 'created':
            new_assignment.workflow.context = order.workflow.context
            new_assignment.workflow.submit()
        new_assignment.workflow.assign(**kwargs)

    @Permission(groups=[G['pm'], G['qa'], G['system'], ])
    def can_reshoot(self):
        """Permission: Validate if user can reshoot an Order.

        Groups: g:pm, g:qa, g:system
        """
        return True

    @in_qa.transition(
        received,
        'can_perm_reject',
        required_fields=PERM_REJECT_REQUIRED_FIELDS
    )
    def perm_reject(self, **kwargs):
        """Transition: Inform the perm rejection of the Assignment.

        Move Order to pending state for a new shoot.
        """
        order = self.document
        order.availability = []
        old_assignment = order.assignment
        create_new_assignment_from_order(
            order,
            order.request,
            copy_payout=True,
            old_assignment=old_assignment
        )
        # force no None value for reason
        if kwargs['fields']['reason_additional_compensation'] == 'null':
            kwargs['fields']['reason_additional_compensation'] = None
            kwargs['fields']['additional_compensation'] = 0
        old_assignment.workflow.perm_reject(**kwargs)
        return True

    @Permission(groups=[LR['project_manager'], G['pm'], G['qa'], ])
    def can_perm_reject(self):
        """Permission: Validate if user can perm_reject an Order.

        Groups: g:pm, g:customers, r:project_manager, r:customer_user
        """
        return True

    @in_qa.transition(
        received,
        'can_new_shoot',
        required_fields=NEWSHOOT_REQUIRED_FIELDS
    )
    @refused.transition(
        received,
        'can_new_shoot',
        required_fields=NEWSHOOT_REQUIRED_FIELDS
    )
    def new_shoot(self, **kwargs):
        """Transition: Inform the new shoot of an Order the customer."""
        message = kwargs.get('message', '')
        order = self.document
        order.availability = []
        old_assignment = order.assignments[-1]
        create_new_assignment_from_order(
            order,
            order.request,
            copy_payout=True,
            old_assignment=old_assignment
        )
        fields = kwargs.get('fields')
        old_assignment.payout_value = fields.get('payout_value')
        old_assignment.travel_expenses = fields.get('travel_expenses')
        old_assignment.workflow.complete(message=message)
        return True

    @Permission(groups=[G['pm'], G['qa'], G['system'], ])
    def can_new_shoot(self):
        """Permission: Validate if user can reshoot an Order.

        Groups: g:pm, g:customers, g:system
        """
        return True

    @delivered.transition(accepted, 'can_accept')
    @refused.transition(accepted, 'can_accept')
    def accept(self, **kwargs):
        """Transition: Customer or PM accept an Order."""
        order = self.document
        for assignment in order.assignments:
            if assignment.state in ('approved', 'refused'):
                # necessary when executing from the task
                if not assignment.workflow.context:
                    assignment.workflow.context = self.context
                message = 'Assignment complete by Order accept transition.'
                assignment.workflow.complete(message=message)

    @Permission(
        groups=[G['pm'], G['customers'], G['system'], ]
    )
    def can_accept(self):
        """Permission: Validate if user can accept an Order.

        Groups: g:pm, g:customers, g:system, r:customer_user, r:project_manager
        """
        order = self.document
        states = ('cancelled', 'perm_rejected', 'completed', 'approved', 'refused')
        for assignment in order.assignments:
            if assignment.state not in states:
                return False
        return True

    @refused.transition(perm_refused, 'can_perm_refuse', message_required=True)
    def perm_refuse(self, **kwargs):
        """Transition: PM permanently refuse an Order."""
        order = self.document
        assignment = order.assignments[-1]
        assignment.workflow.context = self.context
        assignment.workflow.complete()

    @Permission(groups=[G['pm'], G['finance'], G['system']])
    def can_perm_refuse(self):
        """Permission: Validate if user can permanently refuse an Order.

        Groups: g:pm, g:finance and g:system
        """
        order = self.document
        result = True
        assignment = order.assignments[-1] if order.assignments else None
        if not assignment or assignment.state != 'refused':
            result = False
        return result

    @refused.transition(in_qa, 'can_require_revision')
    def require_revision(self, **kwargs):
        """Transition: PM or Customer require revision of an Order."""
        # this should be triggered from the Assignment
        pass

    @Permission(groups=[G['pm'], ])
    def can_require_revision(self):
        """Permission: Validate if user can require revision of an Order."""
        return True
