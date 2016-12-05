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
    history = obj.state_history if hasattr(obj, 'state_history') else []
    valid = [t for t in history if t['transition'] in transitions]
    return valid[order]['date'] if valid else None


def approve_assets_in_job(job: Base, context) -> list:
    """Approve all pending assets in a Job.

    :param job: Internal Briefy Job.
    :param context: Workflow context.
    :returns: List of approved assets in this job.
    """
    all_assets = job.assets
    pending = [
        a for a in all_assets if a.state in ('pending')
    ]
    assets_ids = [a.id for a in all_assets if a.state in ('approved')]
    for asset in pending:
        asset.workflow.context = context
        # Approve asset
        asset.workflow.approve()
        assets_ids.append(asset.id)

    logger.info(
        'Transitioned {assets_count} assets to approved for job {id}'.format(
            assets_count=len(pending),
            id=job.id,
        )
    )
    return assets_ids
