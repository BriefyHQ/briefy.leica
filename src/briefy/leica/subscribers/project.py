"""Event subscribers for briefy.leica.models.project.Project."""
from briefy.leica.events import project as events
from pyramid.events import subscriber


@subscriber(events.ProjectCreatedEvent)
def project_created_handler(event):
    """Handle Project created event."""
    obj = event.obj

    # submit Project after creation
    obj.workflow.start()
