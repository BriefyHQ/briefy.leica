"""Event subscribers for briefy.leica.models.job.Job."""
from briefy.common.users import SystemUser
from briefy.leica.events.job import JobCreatedEvent
from briefy.leica.subscribers import safe_workflow_trigger_transitions
from pyramid.events import subscriber


@subscriber(JobCreatedEvent)
def job_created_handler(event):
    """Handle job created event."""
    transitions = [('submit', ''), ]
    safe_workflow_trigger_transitions(event, transitions=transitions)


def job_submit(event):
    """Handle job submitted event."""
    transitions = []
    # Impersonate the System here
    event.user = SystemUser
    transitions.append(
        ('validate', 'Machine check approved')
    )
    safe_workflow_trigger_transitions(event, transitions=transitions, state='validation')


def transition_handler(event):
    """Handle job transition events."""
    event_name = event.event_name
    if not event_name.startswith('jobassignment.workflow'):
        return

    handlers = {
        'jobassignment.workflow.submit': job_submit
    }
    handler = handlers.get(event_name, None)
    if handler:
        handler(event)
