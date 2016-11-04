"""Event subscribers for briefy.leica.models.job.Job"""
from briefy.common.users import SystemUser
from briefy.leica.events.job import JobCreatedEvent
from briefy.leica.subscribers import safe_workflow_trigger_transitions
from pyramid.events import subscriber


@subscriber(JobCreatedEvent)
def job_created_handler(event):
    """Handle job created event."""
    transitions = [('submit', ''), ]
    safe_workflow_trigger_transitions(event, transitions=transitions)


def job_submit_handler(event):
    """Handle job submitted event."""
    if event.event_name != 'job.workflow.submit':
        return
    transitions = []
    # Impersonate the System here
    event.user = SystemUser
    transitions.append(
        ('validate', 'Machine check approved')
    )
    safe_workflow_trigger_transitions(event, transitions=transitions, state='validation')
