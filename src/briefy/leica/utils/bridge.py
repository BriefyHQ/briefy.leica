"""Bridge helpers between Knack and Briefy."""
from briefy.common.db import Base
from briefy.knack.config import KNACK_API_KEY
from briefy.knack.config import KNACK_APPLICATION_ID

import briefy.knack as K
import logging

logger = logging.getLogger('briefy.leica')
logger.setLevel(logging.INFO)

if KNACK_API_KEY and KNACK_APPLICATION_ID:
    KJob = K.get_model('Job')
else:
    KJob = None


def _get_comments_from_job(job: Base) -> list:
    """Return the list of comment contents for a job.

    :param job: Internal Briefy Job
    :return: List of comment strings
    """
    comments = [c.content for c in job.comments]
    return comments


def get_info_from_job(job: Base) -> dict:
    """Return information about the job."""
    result = {
        'id': job.id,
        'comments': _get_comments_from_job(job),
    }
    return result


def get_knack_job(job_info: dict) -> KJob:
    """Given a information for a Job, return its Knack version.

    :param job_info: Internal Briefy Job information.
    :return: A connect Job on Knack.
    """
    if not KJob:
        raise ValueError('Knack bridge is not configured')

    knack_id = job_info['external_id']
    if not knack_id:
        raise ValueError('Job does not have the equivalent Knack ID')
    return KJob.query.get(knack_id)


def _update_job_on_knack(job_info: dict, knack_state: str):
    """Update a job on Knack.

    :param job_info: Internal Briefy Job information.
    :param state: New knack state
    """
    # concatenate them in a variable
    qa_feedback = '\n\n'.join(job_info['comments'])

    # Get knack job
    knack_job = get_knack_job(job_info)

    # Set values
    knack_job.approval_status = knack_state
    knack_job.quality_assurance_feedback = qa_feedback

    # Update
    K.commit_knack_object(
        knack_job,
        only_fields=(
            'approval_status',
            'quality_assurance_feedback',
        )
    )


def approve_job(job_info: dict):
    """Execute approval methods for job integration on Knack.

    :param job_info: Internal Briefy Job information.
    """
    # Destination state
    knack_state = 'Approved'
    try:
        _update_job_on_knack(job_info, knack_state)
    except Exception:
        logger.exception(
            'Knack: An error occured changing the state of a job to {state}'.format(
                state=knack_state
            )
        )


def reject_job(job_info: dict):
    """Execute approval methods for job integration on Knack.

    :param job_info: Internal Briefy Job information.
    """
    # Destination state
    knack_state = 'Not Approved'
    try:
        _update_job_on_knack(job_info, knack_state)
    except Exception:
        logger.exception(
            'Knack: An error occured changing the state of a job to {state}'.format(
                state=knack_state
            )
        )
