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

    links = request.validated.get('links', None)
    if not obj.links and links:
        # force this because sometimes the obj.id is not available before the flush
        obj.links = links

    # submit for QA validation after creation
    obj.workflow.submit()


def professional_ownership(event):
    """Make sure Professional user is owner of it is own profile."""
    professional = event.obj
    professional_id = professional.id
    owner = professional.owner
    if str(professional_id) != str(owner):
        professional.owner = professional_id


def transition_handler(event):
    """Handle Order transition events."""
    event_name = event.event_name
    if not event_name.startswith('professional.workflow'):
        return
    professional_ownership(event)
