"""Event subscribers for briefy.leica.models.user.UserProfile."""
from briefy.leica.events import professional as events
from pyramid.events import subscriber


@subscriber(events.ProfessionalCreatedEvent)
def professional_created_handler(event):
    """Handle UserProfile created event."""
    obj = event.obj
    request = event.request
    payload = request.validated
    update_kwargs = {}

    main_location = payload.get('main_location', None)
    if not obj.main_location and main_location:
        # force this because sometimes the obj.id is not available before the flush
        update_kwargs['main_location'] = main_location

    links = payload.get('links', None)
    if not obj.links and links:
        # force this because sometimes the obj.id is not available before the flush
        update_kwargs['links'] = links

    # in most of the cases the owner value will not be in the payload
    value = payload.get('owner')
    if not value:
        update_kwargs['owner'] = [obj.id]

    obj.update(update_kwargs)

    # submit for QA validation after creation
    obj.workflow.submit()


def professional_ownership(event):
    """Make sure Professional user is owner of it is own profile."""
    professional = event.obj
    professional_id = professional.id
    owner = professional.owner
    if owner and str(professional_id) not in str(owner[0]):
        professional.update({'owner': [professional_id]})


def transition_handler(event):
    """Handle Professional transition events."""
    event_name = event.event_name
    if not event_name.startswith('professional.workflow'):
        return
    professional_ownership(event)
