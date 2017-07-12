"""Event subscribers for briefy.leica.models.job.leadorder.LeadOrder."""
from briefy.leica.cache import cache_manager
from briefy.leica.events.leadorder import LeadOrderCreatedEvent
from briefy.leica.events.leadorder import LeadOrderUpdatedEvent
from briefy.leica.subscribers import order as order_subscribers
from briefy.leica.subscribers.utils import apply_local_roles_from_parent
from pyramid.events import subscriber


@subscriber(LeadOrderUpdatedEvent)
def leadorder_updated_handler(event):
    """Handle LeadOrder updated event."""
    leadorder = event.obj
    cache_manager.refresh(leadorder)


@subscriber(LeadOrderCreatedEvent)
def leadorder_created_handler(event):
    """Handle LeadOrder created event."""
    leadorder = event.obj
    request = event.request
    project = leadorder.project
    # First set price and price_currency based on the project
    price = project.price
    leadorder.price = price
    leadorder.actual_order_price = 0
    price_currency = project.price_currency
    leadorder.price_currency = price_currency
    if not leadorder.asset_types:
        leadorder.asset_types = project.asset_types[:1]

    add_roles = ('customer_users', 'project_managers')
    apply_local_roles_from_parent(leadorder, project, add_roles)
    location = request.validated.get('location', None)
    if not leadorder.location and location:
        # force this because sometimes the obj.id is not available before the flush
        leadorder.location = location

    # submit the lead order
    leadorder.workflow.submit()
    cache_manager.refresh(leadorder)


def transition_handler(event):
    """Handle LeadOrder transition events."""
    event_name = event.event_name
    if not event_name.startswith('leadorder.workflow'):
        return
    handlers = {
        'leadorder.workflow.cancel': order_subscribers.order_cancel,
        'leadorder.workflow.perm_refuse': order_subscribers.order_perm_refuse,
        'leadorder.workflow.remove_schedule': order_subscribers.order_remove_schedule,
        'leadorder.workflow.refuse': order_subscribers.order_refuse,
        'leadorder.workflow.new_shoot': order_subscribers.order_new_shoot_or_reshoot,
        'leadorder.workflow.reshoot': order_subscribers.order_new_shoot_or_reshoot,
        'leadorder.workflow.unassign': order_subscribers.order_unassign_reassign,
        'leadorder.workflow.reassign': order_subscribers.order_unassign_reassign,
    }
    handler = handlers.get(event_name, None)
    if handler:
        handler(event)

    cache_manager.refresh(event.obj)
