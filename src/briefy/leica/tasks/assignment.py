"""Move Assignments to awaiting assets."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.common.workflow.exceptions import WorkflowTransitionException
from briefy.leica.events.task import LeicaTaskEvent
from briefy.leica.log import tasks_logger as logger
from briefy.leica.models import Assignment


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

    logger.info('Total assignments moved to awaiting assets: {total}'.format(total=total_moved))
