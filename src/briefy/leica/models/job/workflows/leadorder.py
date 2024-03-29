"""Lead Order workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowTransitionException
from briefy.leica.config import ENABLE_LEAD_CONFIRMATION
from briefy.leica.config import LEAD_CONFIRMATION_BYPASS_PROJECTS
from briefy.leica.events.leadorder import LeadOrderUpdatedEvent
from briefy.leica.models.job.workflows.base import BaseOrderWorkflow
from briefy.leica.models.job.workflows.base import REQUIREMENTS_REQUIRED_FIELDS
from briefy.leica.subscribers.utils import create_new_assignment_from_order
from briefy.leica.utils.transitions import get_transition_date_from_history
from briefy.ws.errors import ValidationError


def lead_confirmation_enabled(project_id: str) -> bool:
    """Flag indicating if we are accepting new Orders.

    :return: Boolean
    """
    project_bypass = project_id in LEAD_CONFIRMATION_BYPASS_PROJECTS
    return ENABLE_LEAD_CONFIRMATION or project_bypass


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
        if not lead_confirmation_enabled(str(project.id)):
            raise WorkflowTransitionException('Lead order confirmation is not enabled')
        needed_fields = project.leadorder_confirmation_fields or []
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

        # Set actual_order_price
        leadorder.actual_order_price = leadorder.price
        # Set the current type to order
        leadorder.current_type = 'order'
        if not leadorder.assignments:
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
        order.current_type = 'leadorder'
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
        optional_fields=REQUIREMENTS_REQUIRED_FIELDS
    )
    def edit_requirements(self, **kwargs):
        """Update requirements in a LeadOrder."""
        project_type = self.document.project.project_type
        fields = kwargs.get('fields', {})
        requirements = fields.get('requirements', None)
        number_required_assets = fields.get('number_required_assets', None)
        requirement_items = fields.get('requirement_items', None)
        if (project_type == 'on-demand') and not number_required_assets:
            raise WorkflowTransitionException(
                f'Field number_required_assets is required for this transition'
            )
        elif (project_type == 'on-demand') and not requirements:
            raise WorkflowTransitionException(
                f'Field requirements is required for this transition'
            )
        elif (project_type == 'city') and not requirement_items:
            raise WorkflowTransitionException(
                f'Field requirement_items is required for this transition'
            )
