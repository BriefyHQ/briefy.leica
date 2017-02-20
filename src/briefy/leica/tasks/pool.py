"""Move Assignment to Pool."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.leica import logger
from briefy.leica.models import Order
from briefy.leica.models import Project
from dateutil.parser import parse


def move_assignment_to_pool():
    """Move Assignments from pending to published and set the pool_id."""
    pool_projects = Project.query().filter(Project.pool_id.isnot(None)).all()

    for project in pool_projects:
        orders = Order.query().filter(
            Order.state == 'received',
            Order.project == project
        ).all()

        for order in orders:
            now = datetime_utcnow()
            if order.availability:
                has_availability = False
                for date in order.availability:
                    date = parse(date)
                    date_diff = date - now
                    if date_diff.days >= 2:
                        has_availability = True

                assignment = order.assignment
                has_payout = assignment.payout_value and assignment.payout_currency
                print_msg = True

                if assignment.state != 'pending':
                    print_msg = False
                elif not has_availability:
                    msg = 'Assignment {id} has no availability two days in future.'
                elif assignment.pool_id:
                    msg = 'Assignment {id} is pending but already has a pool id.'
                elif not has_payout:
                    msg = 'Assignment {id} do not have payout information.'
                else:
                    wf = assignment.workflow
                    wf.context = SystemUser
                    fields = dict(pool_id=project.pool_id)
                    transition_message = 'Assignment published in Pool: {pool_name}'
                    transition_message = transition_message.format(pool_name=project.pool.title)
                    wf.publish(fields=fields, message=transition_message)
                    msg = 'Assignment {id} moved to published.'

                if print_msg:
                    msg = msg.format(id=assignment.id)
                    logger.info(msg)
