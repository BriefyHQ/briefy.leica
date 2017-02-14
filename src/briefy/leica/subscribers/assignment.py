"""Event subscribers for briefy.leica.models.job.Assignment."""
# from briefy.common.config import ENV
from briefy.common.users import SystemUser
from briefy.common.vocabularies.roles import Groups as G
from briefy.leica.events.assignment import AssignmentCreatedEvent
from briefy.leica.models import Professional
from briefy.leica.subscribers import safe_workflow_trigger_transitions
from briefy.leica.subscribers.utils import apply_local_roles_from_parent
from briefy.leica.subscribers.utils import create_new_assignment_from_order
from briefy.leica.subscribers.utils import create_comment_from_wf_transition
from pyramid.events import subscriber


@subscriber(AssignmentCreatedEvent)
def assignment_created_handler(event):
    """Handle Assignment created event."""
    assignment = event.obj
    order = assignment.order
    add_roles = ('project_managers', )
    apply_local_roles_from_parent(assignment, order, add_roles)
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


def assignment_perm_reject(event):
    """Handle Assignment perm_reject workflow event."""
    request = event.request
    assignment = event.obj

    # TODO: test if this cause circular failure
    order = assignment.order
    # just create a new Assignment if there is no active assignment
    if not order.assignment and order.state not in ('cancelled', 'perm_refused'):
        create_new_assignment_from_order(order, request)

    to_role = 'professional_user'
    author_role = 'qa_manager'
    create_comment_from_wf_transition(
        assignment,
        author_role,
        to_role
    )


def assignment_remove_schedule(event):
    """Handle Assignment remove_schedule workflow event."""
    assignment = event.obj
    user = assignment.workflow.context

    # this should be always in the subscriber
    # to avoid loop with the order remove_schedule
    order = assignment.order
    message = assignment.state_history[-1]['message']
    if order.state == 'scheduled':
        order.workflow.remove_schedule(message=message)

    # create the comment
    if G['customers'].value in user.groups:
        # this should not create a comment on the assignment only on the order
        return
    elif G['pm'].value in user.groups:
        to_role = 'professional_user'
        author_role = 'project_manager'
    elif G['professionals'].value in user.groups:
        to_role = 'project_manager'
        author_role = 'professional_user'
    else:
        to_role = 'professional_user'
        author_role = 'project_manager'

    create_comment_from_wf_transition(assignment, author_role, to_role)


def assignment_reschedule(event):
    """Handle Assignment reschedule workflow event."""
    assignment = event.obj
    user = assignment.workflow.context

    if G['pm'].value in user.groups:
        to_role = 'professional_user'
        author_role = 'project_manager'
    elif G['professionals'].value in user.groups:
        to_role = 'project_manager'
        author_role = 'professional_user'
    else:
        to_role = 'professional_user'
        author_role = 'project_manager'

    create_comment_from_wf_transition(assignment, author_role, to_role)


def assignment_schedule(event):
    """Handle Assignment schedule workflow event."""
    assignment = event.obj
    user = assignment.workflow.context
    if G['pm'].value in user.groups:
        to_role = 'professional_user'
        author_role = 'project_manager'
    elif G['professionals'].value in user.groups:
        to_role = 'project_manager'
        author_role = 'professional_user'
    else:
        to_role = 'professional_user'
        author_role = 'project_manager'

    create_comment_from_wf_transition(assignment, author_role, to_role)


def assignment_self_assign(event):
    """Handle Assignment self_assign workflow event."""
    assignment = event.obj
    # make sure it will only try to schedule assigned assignment
    if assignment.state == 'assigned':
        fields = dict(scheduled_datetime=assignment.scheduled_datetime)
        assignment.workflow.schedule(fields=fields)


def assignment_scheduling_issues(event):
    """Handle Assignment scheduling_issues workflow event."""
    assignment = event.obj
    user = assignment.workflow.context
    to_role = 'project_manager'
    author_role = 'professional_user'
    internal = False
    professional = Professional.get(user.id)
    if not professional:
        author_role = 'project_manager'
        to_role = 'professional_user'
        internal = True
    create_comment_from_wf_transition(
        assignment,
        author_role,
        to_role,
        internal=internal,
    )


def assignment_reject(event):
    """Handle Assignment reject workflow event."""
    assignment = event.obj
    author_role = 'qa_manager'
    to_role = 'professional_user'
    create_comment_from_wf_transition(
        assignment,
        author_role,
        to_role
    )


def assignment_upload(event):
    """Handle Assignment upload workflow event."""
    assignment = event.obj
    workflow = assignment.workflow
    user = workflow.context
    to_role = 'qa_manager'
    professional = Professional.get(user.id)
    if professional:
        author_role = 'professional_user'
        internal = False
    else:
        author_role = 'project_manager'
        internal = True
    create_comment_from_wf_transition(
        assignment,
        author_role,
        to_role,
        internal=internal
    )
    # TODO: remove this when real machine validation will be activated
    # if assignment.state == 'asset_validation' and ENV in ('staging', 'development'):
    #    workflow.context = SystemUser
    #    workflow.validate_assets(message='Stub machine validation for test only! :)')


def assignment_validate_or_invalidate_assets(event):
    """Handle Assignment validate or invalidate assets workflow event."""
    assignment = event.obj
    author_role = 'qa_manager'
    to_role = 'professional_user'
    create_comment_from_wf_transition(
        assignment,
        author_role,
        to_role,
        internal=False
    )


def assignment_return_to_qa(event):
    """Handle Assignment return_to_qa workflow event."""
    assignment = event.obj
    author_role = 'project_manager'
    to_role = 'qa_manager'
    create_comment_from_wf_transition(
        assignment,
        author_role,
        to_role,
        internal=True
    )


def transition_handler(event):
    """Handle Assignment transition events."""
    event_name = event.event_name
    if not event_name.startswith('assignment.workflow'):
        return

    handlers = {
        'assignment.workflow.submit': assignment_submit,
        'assignment.workflow.perm_reject': assignment_perm_reject,
        'assignment.workflow.self_assign': assignment_self_assign,
        'assignment.workflow.assign_pool': assignment_self_assign,
        'assignment.workflow.scheduling_issues': assignment_scheduling_issues,
        'assignment.workflow.reject': assignment_reject,
        'assignment.workflow.upload': assignment_upload,
        'assignment.workflow.invalidate_assets': assignment_validate_or_invalidate_assets,
        'assignment.workflow.validate_assets': assignment_validate_or_invalidate_assets,
        'assignment.workflow.return_to_qa': assignment_return_to_qa,
        'assignment.workflow.remove_schedule': assignment_remove_schedule,
        'assignment.workflow.reschedule': assignment_reschedule,
        'assignment.workflow.schedule': assignment_schedule,
    }
    handler = handlers.get(event_name, None)
    if handler:
        handler(event)
