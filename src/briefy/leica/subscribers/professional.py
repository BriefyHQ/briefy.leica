"""Event subscribers for briefy.leica.models.user.UserProfile."""
from briefy.leica.events import professional as events
from pyramid.events import subscriber


@subscriber(events.ProfessionalCreatedEvent)
def professional_created_handler(event):
    """Handle UserProfile created event."""
    obj = event.obj
    request = event.request

    location = request.validated.get('main_location', None)
    if not obj.main_location and location:
        # force this because sometimes the obj.id is not available before the flush
        obj.main_location = location

    # submit for QA validation after creation
    obj.workflow.submit()
