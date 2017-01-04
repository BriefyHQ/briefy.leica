"""Event subscribers for briefy.leica.models.job.Assignment."""
from briefy.common.users import SystemUser
from briefy.leica.events.assignment import AssignmentCreatedEvent
from briefy.leica.subscribers import safe_workflow_trigger_transitions
from pyramid.events import subscriber


@subscriber(AssignmentCreatedEvent)
def assignment_created_handler(event):
    """Handle Assignment created event."""
    transitions = [('submit', ''), ]
    safe_workflow_trigger_transitions(event, transitions=transitions)


def assignment_submit(event):
    """Handle Assignment submitted event."""
    transitions = []
    # Impersonate the System here
    event.user = SystemUser
    transitions.append(
        ('validate', 'Machine check approved')
    )
    safe_workflow_trigger_transitions(event, transitions=transitions, state='validation')


def transition_handler(event):
    """Handle Assignment transition events."""
    event_name = event.event_name
    if not event_name.startswith('assignment.workflow'):
        return

    handlers = {
        'assignment.workflow.submit': assignment_submit
    }
    handler = handlers.get(event_name, None)
    if handler:
        handler(event)
