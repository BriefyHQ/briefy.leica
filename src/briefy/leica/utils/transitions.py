"""Transition helpers for Leica."""
from briefy.common.db import Base
from briefy.leica import logger
from datetime import datetime


def get_transition_date(transitions: tuple, obj, first: bool=False) -> datetime:
    """Return the datetime for a named transition.

    Return None if transition never occured.
    :param transition: List of Transitions names.
    :param obj: Workflow aware object.
    :param first: Return the first occurence of this transition.
    """
    order = 0 if first else -1
    history_attr = getattr(obj, 'state_history', None)
    valid_history_attr = history_attr and isinstance(history_attr, list)
    history = obj.state_history if valid_history_attr else []
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
