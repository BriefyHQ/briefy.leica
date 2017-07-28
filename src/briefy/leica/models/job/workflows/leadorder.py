"""Lead Order workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowTransitionException
from briefy.leica.events.leadorder import LeadOrderUpdatedEvent
from briefy.leica.models.job.workflows.base import BaseOrderWorkflow
from briefy.leica.models.job.workflows.base import REQUIREMENTS_REQUIRED_FIELDS
from briefy.leica.subscribers.utils import create_new_assignment_from_order
from briefy.leica.utils.transitions import get_transition_date_from_history
from briefy.ws.errors import ValidationError


class LeadOrderWorkflow(BaseOrderWorkflow):
    """Workflow for a Lead."""

    entity = 'lead'
    initial_state = 'created'
    update_event = LeadOrderUpdatedEvent

    # States
    created = WS(
        'created', 'Created',
        'Order created.'
    )

    new = WS(
        'new', 'New',
        'LeadOrder New.'
    )

    received = BaseOrderWorkflow.received
    cancelled = BaseOrderWorkflow.cancelled

    # Transitions
    @created.transition(new, 'can_submit')
    def submit(self, **kwargs):
        """Submit a LeadOrder."""
        pass

    @Permission(groups=[G['customers'], G['pm'], G['bizdev'], G['system'], ])
    def can_submit(self):
        """Validate if user can submit a LeadOrder."""
        return True

    @new.transition(
        cancelled,
        'can_cancel',
        message_required=True
    )
    def cancel(self, **kwargs):
        """Transition: Cancel the LeadOrder."""
        leadorder = self.document
        assignments = leadorder.assignments
        availability = leadorder.availability
        if not availability:
            leadorder.current_type = 'leadorder'
        if assignments:
            assignment = leadorder.assignments[-1]
            wkf = assignment.workflow
            wkf.context = self.context
            assignment.workflow.cancel()

    @new.transition(
        received,
        'can_confirm',
        optional_fields=('availability', )
    )
    def confirm(self, **kwargs):
        """Confirm LeadOrder and set availability dates."""
        leadorder = self.document
        project = leadorder.project
        needed_fields = project.leadorder_confirmation_fields
        fields = kwargs.get('fields', {})
        for fieldname in needed_fields:
            value = fields.get(fieldname, [])
            if not value:
                raise WorkflowTransitionException(
                    f'Field {fieldname} is required for this transition'
                )
            else:
                payload = {fieldname: value}
                try:
                    leadorder.update(payload)
                except ValidationError as exc:
                    raise WorkflowTransitionException(exc.message)

        state_history = leadorder.state_history
        # Set actual_order_price
        leadorder.actual_order_price = leadorder.price
        # Set the current type to order
        leadorder.current_type = 'order'
        if state_history[-1]['from'] == 'created':
            create_new_assignment_from_order(leadorder, leadorder.request)

    @Permission(groups=[G['customers'], G['pm'], G['bizdev'], G['system'], ])
    def can_confirm(self):
        """Validate if user can confirm a LeadOrder."""
        return True

    @received.transition(
        new,
        'can_remove_confirmation',
    )
    def remove_confirmation(self, **kwargs):
        """Remove LeadOrder confirmation and clean availability dates."""
        order = self.document
        order.availability = None

        # Set actual_order_price
        order.actual_order_price = 0

    @Permission(groups=[
        G['customers'], G['pm'], G['bizdev'], G['tech'], G['product'], G['support'], G['system'],
    ])
    def can_remove_confirmation(self):
        """Validate if user can remove_confirmation of a LeadOrder."""
        leadorder = self.document
        permission = True
        for assignment in leadorder.assignments:
            transitions = ('assign', 'self_assign', 'assign_pool', )
            date = get_transition_date_from_history(
                transitions,
                assignment.state_history,
                first=True
            )
            if date:
                permission = False
                break

        return permission

    @new.transition(
        new,
        'can_edit_location',
        required_fields=('location', )
    )
    def edit_location(self, **kwargs):
        """Update location of a LeadOrder."""
        leadorder = self.document
        location = leadorder.location
        if location:
            payload = kwargs['fields']['location']
            for key, value in payload.items():
                setattr(location, key, value)

            kwargs['fields'] = dict(location=location)

    @new.transition(
        new,
        'can_edit_requirements',
        required_fields=REQUIREMENTS_REQUIRED_FIELDS
    )
    def edit_requirements(self, **kwargs):
        """Update requirements in an LeadOrder."""
        pass
