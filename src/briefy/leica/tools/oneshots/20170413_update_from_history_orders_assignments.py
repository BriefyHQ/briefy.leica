"""Update Orders and Assignments after adding new columns."""
from briefy.leica.db import Session
from briefy.leica.models import Assignment
from briefy.leica.models import Order
from briefy.leica.sync.db import configure
from briefy.leica.tools import logger
import transaction


def update_from_history(model, session):
    """Update from history all records from a given model."""
    all = session.query(model.id).all()
    name = model.__name__
    logger.info('Will process {0} {1}'.format(len(all), name))
    for idx, item in enumerate(all):
        # History
        item = model.get(item[0])
        item._update_dates_from_history()
        logger.info('{0} {1} updated.'.format(name, idx))
        if idx % 10 == 0:
            transaction.commit()

    return idx


def update_orders(session):
    """Update Order dates."""
    total = update_from_history(Order, session)
    logger.info('Finished processing {0} orders.'.format(total))


def update_assignments(session):
    """Update Assignments dates."""
    total = update_from_history(Assignment, session)
    logger.info('Finished processing {0} assignments.'.format(total))


if __name__ == '__main__':
    session = configure(Session)
    update_orders(session)
    update_assignments(session)
    transaction.commit()
