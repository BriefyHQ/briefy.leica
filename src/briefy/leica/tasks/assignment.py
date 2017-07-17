"""Move Assignments to awaiting assets."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.common.workflow.exceptions import WorkflowTransitionException
from briefy.leica.cache import cache_region
from briefy.leica.events.task import LeicaTaskEvent
from briefy.leica.log import tasks_logger as logger
from briefy.leica.models import Assignment
from briefy.leica.models import Comment
from datetime import timedelta
from sqlalchemy import and_
from sqlalchemy import not_


LATE_SUBMISSION_MSG = '** notify task **: The creative was notified about late submission.'


def _move_assignment_awaiting_assets(assignment: Assignment) -> bool:
    """Move Assignments from scheduled to awaiting_assets.

    Task name: leica.task.assignment_awaiting_assets
    Task events:

        * leica.task.assignment_awaiting_assets.success
        * leica.task.assignment_awaiting_assets.failure

    :param assignment: Assignment to be processed
    :return: Status of the transition
    """
    task_name = 'leica.task.assignment_awaiting_assets'
    now = datetime_utcnow()
    status = False
    if assignment.state == 'scheduled' and assignment.scheduled_datetime < now:
        wf = assignment.workflow
        wf.context = SystemUser
        try:
            wf.ready_for_upload()
        except WorkflowTransitionException as e:
            logger.exception(
                'Assignment {id} not moved to awaiting_assets.'.format(id=assignment.id)
            )
        else:
            status = True
            logger.info(
                'Assignment {id} moved to awaiting_assets. Shoot time: {shoot_time}'.format(
                    id=assignment.id,
                    shoot_time=assignment.scheduled_datetime
                )
            )

        cache_region.invalidate(assignment)

        event = LeicaTaskEvent(task_name=task_name, success=status, obj=assignment)
        event()

    return status


def move_assignments_awaiting_assets():
    """Move Assignments from scheduled to awaiting_assets."""
    now = datetime_utcnow()
    assignments = Assignment.query().filter(
        Assignment.scheduled_datetime < now,
        Assignment.state == 'scheduled'
    ).all()

    logger.info('Total assignments to be moved: {size}'.format(size=len(assignments)))

    total_moved = 0

    for assignment in assignments:
        status = _move_assignment_awaiting_assets(assignment)
        total_moved += 1 if status else 0
        cache_region.invalidate(assignment)

    logger.info('Total assignments moved to awaiting assets: {total}'.format(total=total_moved))


def _notify_late_submissions(assignment: Assignment) -> bool:
    """Create a new comment to let professionals know that 48hs passed after the shoot.

    Task name: leica.task.notify_late_submission
    Task events:

        * leica.task.notify_late_submission.success
        * leica.task.notify_late_submission.failure
        * leica.task.notify_late_resubmission.success
        * leica.task.notify_late_resubmission.failure

    :param assignment: Assignment to be processed
    :return: True if the notify comment was registered in the Assignment.
    """
    status = False
    delta = timedelta(seconds=48*3600)
    now = datetime_utcnow()
    has_notify_comment = assignment.comments.filter(
        Comment.content == LATE_SUBMISSION_MSG
    ).all()
    notify_datetime = assignment.scheduled_datetime + delta
    if assignment.state != 'awaiting_assets' or has_notify_comment or notify_datetime > now:
        return status

    payload = dict(
        entity_id=assignment.id,
        entity_type=assignment.__class__.__name__,
        author_id=SystemUser.id,
        content=LATE_SUBMISSION_MSG,
        author_role='project_manager',
        to_role='professional_user',
        internal=True,
    )
    try:
        comment = Comment(**payload)
        session = assignment.__session__
        session.add(comment)
        assignment.comments.append(comment)
        session.flush()
    except Exception as exc:
        msg = 'Failure to add comment to assignment: {id}. Error: {exception}'
        logger.error(msg.format(id=assignment.id, exc=str(exc)))
        return status
    else:
        cache_region.invalidate(assignment)
        status = True
        task_name = 'leica.task.notify_late_submission'
        event = LeicaTaskEvent(task_name=task_name, success=status, obj=assignment)
        event()
        return status


def notify_late_submissions():
    """Search assignments with late submissions to be notified."""
    delta = timedelta(seconds=48*3600)
    now = datetime_utcnow()
    query = Assignment.query().filter(
        and_(
            Assignment.state == 'awaiting_assets',
            not_(Assignment.comments.any(Comment.content == LATE_SUBMISSION_MSG))
        )
    )
    assignments = [a for a in query if (a.scheduled_datetime + delta) < now]
    msg = 'Total assignments professionals will  be notified for late submissions: {size}'
    logger.info(msg.format(size=len(assignments)))

    total_notified = 0
    for assignment in assignments:
        status = _notify_late_submissions(assignment)
        total_notified += 1 if status else 0

    msg = 'Total of assignments professional was notified for late submission: {total}'
    logger.info(msg.format(total=total_notified))
