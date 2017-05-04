"""Order tasks."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.leica.cache import cache_region
from briefy.leica.events.task import LeicaTaskEvent
from briefy.leica.log import tasks_logger as logger
from briefy.leica.models import Order
from workdays import workday


def _move_order_accepted(order: Order) -> bool:
    """Move Order from delivered to accepted after a certain amount of working days.

    Task name: leica.task.order_accepted
    Task events:

        * leica.task.order_accepted.success
        * leica.task.order_accepted.failure

    :param order: Order to be processed.
    :return: Status of the transition
    """
    task_name = 'leica.task.order_accepted'
    status = False
    state = order.state
    last_deliver_date = order.last_deliver_date
    if (state == 'delivered' and last_deliver_date):
        now = datetime_utcnow()
        project = order.project
        approval_window = project.approval_window
        allowed_accept_date = workday(last_deliver_date, approval_window)
        wf = order.workflow
        wf.context = SystemUser

        if now >= allowed_accept_date:
            if not wf.can_accept:
                assignment_states = [a.state for a in order.assignments]
                msg = 'Approval window for Order {id} expired but it can not be completed. ' \
                      'Assignment states: {states}'
                msg = msg.format(id=order.id, states=str(assignment_states))
            else:
                wf.accept(message='Order automatic accepted after the end of the approval window.')
                msg = 'Order {id} moved to completed. Delivery date: {deliver_date}'
                msg = msg.format(id=order.id, deliver_date=last_deliver_date)
                status = True

            # Trigger task event
            cache_region.invalidate(order)
            event = LeicaTaskEvent(task_name=task_name, success=status, obj=order)
            event()
            logger.info(msg)
    return status


def move_orders_accepted():
    """Move Orders from delivered to accepted."""
    orders = Order.query().filter(Order.state == 'delivered').all()

    logger.info('Total orders in delivered state: {total}'.format(total=len(orders)))

    total_moved = 0
    for order in orders:
        status = _move_order_accepted(order)
        total_moved += 1 if status else 0
        cache_region.invalidate(order)

    logger.info('Total orders moved to accepted state: {total}'.format(total=total_moved))
