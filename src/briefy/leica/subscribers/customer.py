"""Event subscribers for briefy.leica.models.customer.Customer."""
from briefy.leica.events import customer as events
from pyramid.events import subscriber


@subscriber(events.CustomerCreatedEvent)
def customer_created_handler(event):
    """Handle Customer created event."""
    obj = event.obj

    # submit customer after creation
    obj.workflow.submit()
