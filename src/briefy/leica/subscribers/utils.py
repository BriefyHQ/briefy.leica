"""Utils functions for subscribers."""
from briefy.leica.events.assignment import AssignmentCreatedEvent
from briefy.leica.models import Assignment
from briefy.leica.models import Comment
from sqlalchemy.orm.session import object_session


def create_comment_from_wf_transition(obj, author_role, to_role, internal=False):
    """Create a new Comment instance from the last workflow transition."""
    session = object_session(obj)
    last_transition = obj.state_history[-1]
    message = last_transition['message']
    user_id = last_transition['actor']
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
