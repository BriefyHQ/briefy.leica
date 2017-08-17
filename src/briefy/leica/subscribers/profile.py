"""Event subscribers for briefy.leica.models.user.UserProfile."""
from briefy.leica.events import userprofile as events
from pyramid.events import subscriber


@subscriber(events.UserProfileCreatedEvent)
def userprofile_created_handler(event):
    """Handle UserProfile created event."""
    obj = event.obj
    request = event.request
    payload = request.validated
    update_kwargs = {}

    if obj.type == 'customeruserprofile':
        # force this because sometimes the obj.id is not available before the flush
        pop_attrs = ['project_customer_qa', 'project_customer_pm', 'customer_roles']
        for attr in pop_attrs:
            value = payload.get(attr)
            if value:
                update_kwargs[attr] = value

    # in most of the cases the owner value will not be in the payload
    value = payload.get('owner')
    if not value:
        update_kwargs['owner'] = [obj.id]

    obj.update(update_kwargs)

    # activate the user after creation
    obj.workflow.activate()
