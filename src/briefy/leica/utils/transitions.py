"""Transition helpers for Leica."""
from briefy.common.db import Base
from briefy.leica import logger
from datetime import datetime
from sqlalchemy.orm.session import object_session


def get_transition_date(transitions: tuple, obj, first: bool=False) -> datetime:
    """Return the datetime for a named transition.

    Return None if transition never occured.
    :param transitions: List of Transitions names.
    :param obj: Workflow aware object.
    :param first: Return the first occurence of this transition.
    """
    history_attr = getattr(obj, 'state_history', None)
    return get_transition_date_from_history(
        transitions, history_attr, first
    )


def get_transition_date_from_history(
        transitions: tuple, history: list, first: bool=False
) -> datetime:
    """Return the datetime for a named transition.

    Return None if transition never occurred.
    :param transitions: List of Transitions names.
    :param history: Workflow history.
    :param first: Return the first occurrence of this transition.
    """
    order = 0 if first else -1
    valid_history_attr = history and isinstance(history, list)
    history = history if valid_history_attr else []
    valid = [t for t in history if t['transition'] in transitions]
    return valid[order]['date'] if valid else None


def approve_assets_in_assignment(assignment: Base, context) -> list:
    """Approve all pending assets in an Assignment.

    :param assignment: Internal Briefy Assignment.
    :param context: Workflow context.
    :returns: List of approved assets in this assignment.
    """
    all_assets = assignment.assets
    pending = [
        a for a in all_assets if a.state == 'pending'
    ]
    assets_ids = [a.id for a in all_assets if a.state == 'approved']
    for asset in pending:
        asset.workflow.context = context
        # Approve asset
        asset.workflow.approve()
        assets_ids.append(asset.id)

    logger.info(
        'Transitioned {assets_count} assets to approved for Assignment {id}'.format(
            assets_count=len(pending),
            id=assignment.id,
        )
    )
    return assets_ids


def create_comment_on_assignment_approval(assignment, actor, message):
    """Create a new Comment instance from the last workflow transition."""
    from briefy.leica.models import Comment

    session = object_session(assignment)
    order = assignment.order
    user_id = actor['id'] if isinstance(actor, dict) else actor
    author_role = 'qa_manager'
    to_role = 'customer_user'
    if message:
        payload = dict(
            entity_id=order.id,
            entity_type=order.__class__.__name__,
            author_id=user_id,
            content=message,
            author_role=author_role,
            to_role=to_role,
            internal=False,
        )
        comment = Comment(**payload)
        session.add(comment)
