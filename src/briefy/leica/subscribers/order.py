"""Event subscribers for briefy.leica.models.job.Order."""
from briefy.common.users import SystemUser
from briefy.leica.events.order import OrderCreatedEvent
from briefy.leica.subscribers.utils import create_new_assignment_from_order
from briefy.leica.subscribers.utils import create_comment_from_wf_transition
# from briefy.leica.subscribers import safe_workflow_trigger_transitions
from pyramid.events import subscriber


@subscriber(OrderCreatedEvent)
def order_created_handler(event):
    """Handle Order created event."""
    order = event.obj
    request = event.request
    # create a new assignment
    create_new_assignment_from_order(order, request)
    # submit the order
    order.workflow.submit()


def order_submit(event):
    """Handle Order submitted event."""
    transitions = []
    # Impersonate the System here
    event.user = SystemUser
    transitions.append(
        ('validate', 'Machine check approved')
    )
    # do nothing for while
    # safe_workflow_trigger_transitions(event, transitions=transitions, state='validation')


def order_cancel_or_perm_refuse(event):
    """Handle Assignment cancel and perm_reject workflow event."""
    order = event.obj
    request = event.request
    # cancel all existing assignments
    for assignment in order.assignments:
        assignment.workflow.cancel()

    author_role = 'customer_user'
    to_role = 'project_manager'
    create_comment_from_wf_transition(order, request, author_role, to_role)


def order_remove_schedule(event):
    """Handle Order remove_schedule workflow event."""
    order = event.obj
    assignment = order.assignment
    assignment.scheduled_datetime = None
    if assignment.state == 'scheduled':
        order.workflow.remove_schedule()


def order_refuse(event):
    """Handle Order refuse workflow event."""
    order = event.obj
    request = event.request
    author_role = 'customer_user'
    to_role = 'project_manager'
    create_comment_from_wf_transition(order, request, author_role, to_role)


def order_new_shoot_or_reshoot(event):
    """Handle Order new_shoot reshoot workflow event."""
    order = event.obj
    request = event.request
    if not order.assignment:
        assignment = create_new_assignment_from_order(order, request)
        # assign the new assignment to the previous professional
        if order.state == 'assigned':
            last_assignment = order.assignment[-1]
            professional_id = last_assignment.professional_id
            fields = dict(professional_id=professional_id)
            assignment.assign(fields=fields)


def transition_handler(event):
    """Handle Assignment transition events."""
    event_name = event.event_name
    if not event_name.startswith('order.workflow'):
        return

    handlers = {
        'order.workflow.submit': order_submit,
        'order.workflow.cancel': order_cancel_or_perm_refuse,
        'order.workflow.perm_refuse': order_cancel_or_perm_refuse,
        'order.workflow.remove_schedule': order_remove_schedule,
        'order.workflow.refuse': order_refuse,
        'order.workflow.new_shoot': order_new_shoot_or_reshoot,
        'order.workflow.reshoot': order_new_shoot_or_reshoot,
    }
    handler = handlers.get(event_name, None)
    if handler:
        handler(event)