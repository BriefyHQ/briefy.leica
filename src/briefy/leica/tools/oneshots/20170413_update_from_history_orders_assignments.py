"""Update Orders and Assignments after adding new columns."""
from briefy.leica.db import Session
from briefy.leica.models import Assignment
from briefy.leica.models import Order
from briefy.leica.sync.db import configure
from briefy.leica.tools import logger
import transaction


def update_from_history(model):
    """Update from history all records from a given model."""
    all = model.query().all()
    logger.info('Will process {0} {1}'.format(len(all), model.__name__))
    for idx, item in enumerate(all):
        # History
        item._update_dates_from_history()

    return idx


def update_orders():
    """Update Order dates."""
    with transaction.manager:
        total = update_from_history(Order)
    logger.info('Finished processing {0} orders.'.format(total))


def update_assignments():
    """Update Assignments dates."""
    with transaction.manager:
        total = update_from_history(Assignment)
    logger.info('Finished processing {0} assignments.'.format(total))


if __name__ == '__main__':
    session = configure(Session)  # no
    update_orders()
    update_assignments()
