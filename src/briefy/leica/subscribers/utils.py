"""Utils functions for subscribers."""
from briefy.leica.events.assignment import AssignmentCreatedEvent
from briefy.leica.models import Assignment
from briefy.leica.models import Comment
from sqlalchemy.orm.session import object_session


def create_comment_from_wf_transition(obj, request, author_role, to_role, internal=False):
    """Create a new Comment instance from the last workflow transition."""
    session = object_session(obj)
    user = request.user
    message = obj.state_history[-1]['message']
    if message:
        payload = dict(
            entity_id=obj.id,
            entity_type=obj.__tablename__,
            author_id=user.id,
            content=message,
            author_role=author_role,
            to_role=to_role,
            internal=internal,
        )
        comment = Comment(**payload)
        session.add(comment)
        session.flush()


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
