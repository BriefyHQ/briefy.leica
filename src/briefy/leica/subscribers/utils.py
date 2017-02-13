"""Utils functions for subscribers."""
from briefy.leica.events.assignment import AssignmentCreatedEvent
from briefy.leica.models import Comment
from sqlalchemy.orm.session import object_session
from sqlalchemy.ext.associationproxy import _AssociationList


def apply_local_roles_from_parent(obj, parent, add_roles=()):
    """Copy local roles from parent."""
    parent_actors = parent.__actors__
    obj_actors = obj.__actors__

    for role in parent_actors:
        if role in obj_actors and role in add_roles:
            parent_role_value = getattr(parent, role)
            obj_role_value = getattr(obj, role)
            if isinstance(parent_role_value, _AssociationList):
                for item in parent_role_value:
                    obj_role_value.append(item)
            else:
                obj_role_value = parent_role_value


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
