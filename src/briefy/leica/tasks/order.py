"""Order tasks."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.leica.log import tasks_logger as logger
from briefy.leica.models import Order

from workdays import workday


def move_order_accepted():
    """Move Order from delivered to accepted."""
    orders = Order.query().filter(
        Order.state == 'delivered'
    ).all()
    msg = 'Total orders in delivered state: {size}'
    msg = msg.format(size=len(orders))
    logger.info(msg)
    total_moved = 0
    for order in orders:
        project = order.project
        last_deliver_date = order.last_deliver_date
        approval_window = project.approval_window
        now = datetime_utcnow()
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
                total_moved += 1

            logger.info(msg)

    msg = 'Total orders moved to accepted state: {size}'
    msg = msg.format(size=total_moved)
    logger.info(msg)
