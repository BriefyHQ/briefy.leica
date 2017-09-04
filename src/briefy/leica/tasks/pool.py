"""Move Assignment to Pool."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.leica.cache import cache_region
from briefy.leica.events.task import LeicaTaskEvent
from briefy.leica.log import tasks_logger as logger
from briefy.leica.models import Assignment
from briefy.leica.models import Order
from briefy.leica.models import Pool
from briefy.leica.models import Project
from dateutil.parser import parse


def _move_assignment_to_pool(assignment: Assignment, pool: Pool, has_availability: bool) -> bool:
    """Move one Assignment to a Pool.

    Task name: leica.task.assignment_pool
    Task events:

        * leica.task.assignment_pool.success
        * leica.task.assignment_pool.no_availability
        * leica.task.assignment_pool.has_pool_id
        * leica.task.assignment_pool.no_payout

    :param assignment: Assignment to be moved to a Pool
    :param pool: Pool to move the assignment to.
    :param has_availability: Does this Assignment have available dates to be published.
    :return: Status of the transition
    """
    task_name = 'leica.task.assignment_pool'
    has_payout = assignment.payout_value and assignment.payout_currency

    status = False
    suffix = ''
    if assignment.state == 'pending':
        if not has_availability:
            msg = 'Assignment {id} has no availability two days in future.'
            suffix = 'no_availability'
        elif assignment.pool_id:
            msg = 'Assignment {id} is pending but already has a pool id.'
            suffix = 'has_pool_id'
        elif not has_payout:
            msg = 'Assignment {id} does not have payout information.'
            suffix = 'no_payout'
        else:
            wf = assignment.workflow
            wf.context = SystemUser
            fields = {'pool_id': pool.id}
            transition_message = 'Assignment published in Pool: {pool_name}'.format(
                pool_name=pool.title
            )
            wf.publish(fields=fields, message=transition_message)

            status = True
            msg = 'Assignment {id} moved to published.'

            cache_region.invalidate(assignment)
            cache_region.invalidate(assignment.order)

        # Trigger task event
        event = LeicaTaskEvent(task_name=task_name, success=status, obj=assignment)
        if suffix:
            event.event_name = event.event_name.replace('failure', suffix)
        event()

        msg = msg.format(id=assignment.id)
        logger.info(msg)
    return status


def move_assignments_to_pool():
    """Move Assignments from pending to published and set the pool_id."""
    pool_projects = Project.query().filter(Project.pool_id.isnot(None)).all()
    now = datetime_utcnow()

    for project in pool_projects:
        pool = project.pool
        orders = Order.query().filter(Order.state == 'received', Order.project == project).all()
        for order in orders:
            availability = order.availability
            if not availability:
                continue

            has_availability = False
            for date in availability:
                date_diff = parse(date) - now
                has_availability = has_availability or (date_diff.days >= 2)

            assignment = order.assignment
            _move_assignment_to_pool(assignment, pool, has_availability)
