"""Event subscribers for briefy.leica.models.user.UserProfile."""
from briefy.leica.events import userprofile as events
from pyramid.events import subscriber


@subscriber(events.UserProfileCreatedEvent)
def userprofile_created_handler(event):
    """Handle UserProfile created event."""
    obj = event.obj
    request = event.request

    if obj.type == 'customeruserprofile':
        # force this because sometimes the obj.id is not available before the flush
        payload = request.validated
        customer_roles = payload.get('customer_roles')
        project_roles = payload.get('project_roles')
        obj.customer_roles = customer_roles
        obj.project_roles = project_roles

    # activate the user after creation
    obj.workflow.activate()
