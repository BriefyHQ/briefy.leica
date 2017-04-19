"""Find and set all missing scout managers in Orders and Assignments."""
from briefy.leica.db import Session
from briefy.leica.models import Assignment
from briefy.leica.models import Order
from briefy.leica.sync.db import configure
from briefy.leica.tools import logger
from sqlalchemy import not_

import transaction


def update_orders_scout_manager():
    """Set scout manager in the orders without."""
    all_orders = Order.query().filter(
        not_(
            Order.state.in_(
                ['received', 'cancelled']
            )
        )
    ).all()

    no_scout_manager = [o.id for o in all_orders if not o.scout_manager]
    total = len(no_scout_manager)
    logger.info('{0} Orders without scout manager will be updated.'.format(total))
    for number, item in enumerate(no_scout_manager):
        order = Order.get(item)
        order.scout_manager = order.project_manager
        logger.info('Scout Manager set on Order {0}'.format(order.id))
        if number % 10 == 0:
            transaction.commit()


def update_assignments_scout_manager():
    """Set scout manager in the assignments without."""
    all_assignments = Assignment.query().filter(
        not_(
            Assignment.state.in_(
                ['pending', 'cancelled']
            )
        )
    ).all()

    no_scout_manager = [o.id for o in all_assignments if not o.scout_manager]
    total = len(no_scout_manager)
    logger.info('{0} Assignments without scout manager will be updated.'.format(total))
    for number, item in enumerate(no_scout_manager):
        assignment = Assignment.get(item)
        order = assignment.order
        order_scout = order.scout_manager
        assignment.scout_manager = order_scout if order_scout else order.project_manager
        logger.info('Scout Manager set on Assignment {0}'.format(assignment.id))
        if number % 10 == 0:
            transaction.commit()

if __name__ == '__main__':
    session = configure(Session)
    update_orders_scout_manager()
    transaction.commit()
    update_assignments_scout_manager()
    transaction.commit()
