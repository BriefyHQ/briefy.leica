"""Utils functions for subscribers."""
from briefy.leica.events.assignment import AssignmentCreatedEvent
from briefy.leica.models import Comment
from briefy.leica.models import LocalRole
from sqlalchemy.orm.session import object_session


def apply_local_roles_from_parent(obj, parent, excludes=()):
    """Copy local roles from parent."""
    local_roles = []
    entity_type = obj.__class__.__name__
    existing = LocalRole.query().filter(
        LocalRole.entity_id == obj.id, LocalRole.entity_type == entity_type
    ).all()
    existing = [(l.user_id, l.role_name.value) for l in existing]
    for lr in parent.local_roles:
        role_name = lr.role_name.value
        key = (lr.user_id, role_name)
        if role_name in excludes or key in existing:
            continue
        payload = dict(
            entity_type=obj.__class__.__name__,
            entity_id=obj.id,
            user_id=lr.user_id,
            role_name=lr.role_name,
            can_create=lr.can_create,
            can_delete=lr.can_delete,
            can_edit=lr.can_edit,
            can_list=lr.can_list,
            can_view=lr.can_view
        )
        local_roles.append(LocalRole(**payload))
    obj.local_roles = local_roles


def create_comment_from_wf_transition(obj, author_role, to_role, internal=False):
    """Create a new Comment instance from the last workflow transition."""
    session = object_session(obj)
    last_transition = obj.state_history[-1]
    message = last_transition['message']
    actor = last_transition['actor']
    user_id = actor['id'] if isinstance(actor, dict) else actor
    # HACK: It is ugly, but worked
    comments = obj.comments.filter(
        Comment.author_id == user_id,
        Comment.content == message,
        Comment.to_role == to_role,
        Comment.author_role == author_role,
    ).count()
    if message and comments == 0:
        payload = dict(
            entity_id=obj.id,
            entity_type=obj.__class__.__name__,
            author_id=user_id,
            content=message,
            author_role=author_role,
            to_role=to_role,
            internal=internal,
        )
        comment = Comment(**payload)
        session.add(comment)


def create_new_assignment_from_order(order, request):
    """Create a new Assignment object from Order."""
    from briefy.leica.models import Assignment
    session = object_session(order)
    payload = {
        'order_id': order.id,
    }
    assignment = Assignment(**payload)
    session.add(assignment)
    session.flush()

    # event dispatch: pyramid event
    assignment_event = AssignmentCreatedEvent(assignment, request)
    request.registry.notify(assignment_event)
    # event dispatch: sqs event
    assignment_event()
    return assignment
