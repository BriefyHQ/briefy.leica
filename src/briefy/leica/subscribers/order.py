"""Event subscribers for briefy.leica.models.job.Order."""
from briefy.common.users import SystemUser
from briefy.common.vocabularies.roles import Groups as G
from briefy.leica.events.order import OrderCreatedEvent
from briefy.leica.subscribers.utils import apply_local_roles_from_parent
from briefy.leica.subscribers.utils import create_new_assignment_from_order
from briefy.leica.subscribers.utils import create_comment_from_wf_transition
# from briefy.leica.subscribers import safe_workflow_trigger_transitions
from pyramid.events import subscriber


@subscriber(OrderCreatedEvent)
def order_created_handler(event):
    """Handle Order created event."""
    order = event.obj
    request = event.request
    project = order.project
    apply_local_roles_from_parent(order, project, ())
    location = request.validated.get('location', None)
    if not order.location and location:
        # force this because sometimes the obj.id is not available before the flush
        order.location = location

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
    author_role = 'customer_user'
    to_role = 'project_manager'
    create_comment_from_wf_transition(order, author_role, to_role)


def order_remove_schedule(event):
    """Handle Order remove_schedule workflow event."""
    order = event.obj
    user = order.workflow.context

    # this should be always in the subscriber
    # to avoid loop with the order remove_schedule
    assignment = order.assignment
    message = order.state_history[-1]['message']
    if assignment.state == 'scheduled':
        assignment.workflow.remove_schedule(message=message)

    # create comment
    if G['customers'].value in user.groups:
        to_role = 'project_manager'
        author_role = 'customer_user'
    elif G['pm'].value in user.groups:
        to_role = 'customer_user'
        author_role = 'project_manager'
    elif G['professionals'].value in user.groups:
        # this should not create a comment on the order only on the assignment
        return
    else:
        to_role = 'customer_user'
        author_role = 'project_manager'

    create_comment_from_wf_transition(
        order,
        author_role,
        to_role
    )


def order_refuse(event):
    """Handle Order refuse workflow event."""
    order = event.obj
    user = order.workflow.context
    if G['customers'].value in user.groups:
        author_role = 'customer_user'
        to_role = 'project_manager'
        internal = False
    else:
        author_role = 'project_manager'
        to_role = 'customer_user'
        internal = True
    create_comment_from_wf_transition(
        order,
        author_role,
        to_role,
        internal=internal
    )


def order_new_shoot_or_reshoot(event):
    """Handle Order new_shoot reshoot workflow event."""
    order = event.obj
    author_role = 'project_manager'
    to_role = 'customer_user'
    create_comment_from_wf_transition(
        order,
        author_role,
        to_role,
        internal=True
    )


def order_unassign(event):
    """Handle Order unassign workflow event."""
    order = event.obj
    author_role = 'project_manager'
    to_role = 'customer_user'
    create_comment_from_wf_transition(
        order,
        author_role,
        to_role,
        internal=True
    )


def transition_handler(event):
    """Handle Cancel transition events."""
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
        'order.workflow.unassign': order_unassign,
    }
    handler = handlers.get(event_name, None)
    if handler:
        handler(event)
