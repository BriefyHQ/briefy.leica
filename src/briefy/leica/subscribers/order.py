"""Event subscribers for briefy.leica.models.job.Order."""
from briefy.common.users import SystemUser
from briefy.common.vocabularies.roles import Groups as G
from briefy.leica.events.order import OrderCreatedEvent
from briefy.leica.subscribers.utils import apply_local_roles_from_parent
from briefy.leica.subscribers.utils import create_new_assignment_from_order
from briefy.leica.subscribers.utils import create_comment_from_wf_transition
from pyramid.events import subscriber


@subscriber(OrderCreatedEvent)
def order_created_handler(event):
    """Handle Order created event."""
    order = event.obj
    request = event.request
    project = order.project
    # First set price and price_currency based on the project
    price = project.price
    order.price = price
    price_currency = project.price_currency
    order.price_currency = price_currency

    add_roles = ('customer_users', 'project_managers')
    apply_local_roles_from_parent(order, project, add_roles)
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


def order_cancel(event):
    """Handle Order cancel workflow event."""
    order = event.obj
    user = order.workflow.context
    if G['customers'].value in user.groups:
        to_role = 'project_manager'
        author_role = 'customer_user'
    elif G['pm'].value in user.groups:
        to_role = 'customer_user'
        author_role = 'project_manager'
    create_comment_from_wf_transition(
        order,
        author_role,
        to_role
    )


def order_perm_refuse(event):
    """Handle Order perm_reject workflow event."""
    order = event.obj
    to_role = 'customer_user'
    author_role = 'project_manager'
    create_comment_from_wf_transition(
        order,
        author_role,
        to_role,
        internal=True
    )


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

    # create the comment if applicable
    if G['customers'].value in user.groups:
        to_role = 'project_manager'
        author_role = 'customer_user'
        create_comment_from_wf_transition(order, author_role, to_role)


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
    """Handle Order new_shoot and reshoot workflow event."""
    order = event.obj
    author_role = 'project_manager'
    to_role = 'customer_user'
    create_comment_from_wf_transition(
        order,
        author_role,
        to_role,
        internal=True
    )


def order_unassign_reassign(event):
    """Handle Order unassign and reassign workflow event."""
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
        'order.workflow.cancel': order_cancel,
        'order.workflow.perm_refuse': order_perm_refuse,
        'order.workflow.remove_schedule': order_remove_schedule,
        'order.workflow.refuse': order_refuse,
        'order.workflow.new_shoot': order_new_shoot_or_reshoot,
        'order.workflow.reshoot': order_new_shoot_or_reshoot,
        'order.workflow.unassign': order_unassign_reassign,
        'order.workflow.reassign': order_unassign_reassign,
    }
    handler = handlers.get(event_name, None)
    if handler:
        handler(event)
