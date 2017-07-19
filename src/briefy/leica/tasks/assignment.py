"""Move Assignments to awaiting assets."""
from briefy.common.users import SystemUser
from briefy.common.workflow.exceptions import WorkflowTransitionException
from briefy.leica.cache import cache_region
from briefy.leica.config import BEFORE_SHOOTING_SECONDS
from briefy.leica.config import LATE_SUBMISSION_SECONDS
from briefy.leica.events.task import LeicaTaskEvent
from briefy.leica.log import tasks_logger as logger
from briefy.leica.models import Assignment
from briefy.leica.models import Comment
from datetime import datetime
from datetime import timedelta
from pytz import timezone
from sqlalchemy import and_
from sqlalchemy import not_


LATE_SUBMISSION_MSG = '** notify task **: The creative was notified about late submission.'
BEFORE_SHOOTING_MSG = '** notify task **: The creative was notified before the shooting.'


def timezone_now(tz: (str, timezone)):
    """Return datetime.now with timezone information."""
    return datetime.now(tz=timezone(str(tz)))


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
    now = timezone_now('UTC')
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
    query = Assignment.query().filter(
        Assignment.state == 'scheduled'
    ).all()

    assignments = []
    for item in query:
        now = timezone_now('UTC')
        if item.scheduled_datetime and item.scheduled_datetime < now:
            assignments.append(item)

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

    :param assignment: Assignment to be processed
    :return: True if a new notify comment was registered in the Assignment.
    """
    status = False
    has_notify_comment = assignment.comments.filter(
        Comment.content == LATE_SUBMISSION_MSG,
        Comment.internal.is_(True),
    ).all()

    now = timezone_now('UTC')
    delta = now - assignment.scheduled_datetime
    config_delta = timedelta(seconds=int(LATE_SUBMISSION_SECONDS))
    should_notify = delta > config_delta
    if assignment.state != 'awaiting_assets' or has_notify_comment or not should_notify:
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
        msg = 'Failure to add comment to assignment: {id}. Error: {exc}'
        logger.error(msg.format(id=assignment.id, exc=str(exc)))
    else:
        cache_region.invalidate(assignment)
        status = True

    task_name = 'leica.task.notify_late_submission'
    event = LeicaTaskEvent(task_name=task_name, success=status, obj=assignment)
    event()
    return status


def notify_late_submissions():
    """Search for assignments with late submissions to be notified."""
    query = Assignment.query().filter(
        and_(
            Assignment.state == 'awaiting_assets',
            not_(Assignment.comments.any(Comment.content == LATE_SUBMISSION_MSG))
        )
    )
    assignments = []
    for item in query:
        now = timezone_now('UTC')
        delta = now - item.scheduled_datetime
        config_delta = timedelta(seconds=int(LATE_SUBMISSION_SECONDS))
        should_notify = delta > config_delta
        if should_notify:
            assignments.append(item)

    msg = 'Total assignments professionals will be notified for late submissions: {size}'
    logger.info(msg.format(size=len(assignments)))

    total_notified = 0
    for assignment in assignments:
        status = _notify_late_submissions(assignment)
        total_notified += 1 if status else 0

    msg = 'Total of assignments professionals were notified for late submission: {total}'
    logger.info(msg.format(total=total_notified))


def _notify_before_shooting(assignment: Assignment) -> bool:
    """Create a new comment to let professionals about scheduled datetime before shooting.

    Task name: leica.task.notify_before_shooting
    Task events:

        * leica.task.notify_before_shooting.success
        * leica.task.notify_before_shooting.failure

    :param assignment: Assignment to be processed
    :return: True if a new notify comment was registered in the Assignment.
    """
    status = False
    now = timezone_now('UTC')
    has_notify_comment = assignment.comments.filter(
        Comment.content == BEFORE_SHOOTING_MSG,
        Comment.internal.is_(True),
    ).all()
    delta = assignment.scheduled_datetime - now
    config_delta = timedelta(seconds=int(BEFORE_SHOOTING_SECONDS))
    should_notify = delta.days >= 0 and delta <= config_delta
    if assignment.state != 'scheduled' or not should_notify or has_notify_comment:
        return status

    payload = dict(
        entity_id=assignment.id,
        entity_type=assignment.__class__.__name__,
        author_id=SystemUser.id,
        content=BEFORE_SHOOTING_MSG,
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
        msg = 'Failure to add comment to assignment: {id}. Error: {exc}'
        logger.error(msg.format(id=assignment.id, exc=str(exc)))
    else:
        cache_region.invalidate(assignment)
        status = True

    task_name = 'leica.task.notify_before_shooting'
    event = LeicaTaskEvent(task_name=task_name, success=status, obj=assignment)
    event()
    return status


def notify_before_shooting():
    """Search for assignments scheduled and notify professional before shooting."""
    query = Assignment.query().filter(
        and_(
            Assignment.state == 'scheduled',
            not_(Assignment.comments.any(Comment.content == BEFORE_SHOOTING_MSG))
        )
    )
    assignments = []
    for item in query:
        now = timezone_now('UTC')
        delta = item.scheduled_datetime - now
        config_delta = timedelta(seconds=int(BEFORE_SHOOTING_SECONDS))
        should_notify = delta.days >= 0 and delta <= config_delta
        if should_notify:
            assignments.append(item)

    msg = 'Total assignments professionals will be notified before shooting: {size}'
    logger.info(msg.format(size=len(assignments)))

    total_notified = 0
    for assignment in assignments:
        status = _notify_before_shooting(assignment)
        total_notified += 1 if status else 0

    msg = 'Total of assignments professionals were notified before shooting: {total}'
    logger.info(msg.format(total=total_notified))
