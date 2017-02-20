"""Update Orders and Assignments after adding new columns."""
from briefy.leica.db import Session
from briefy.leica.models import Order
from briefy.leica.sync.db import configure
from briefy.leica.tools import logger
import transaction


def main():
    """Update Order dates."""
    session = configure(Session)  # noqa
    with transaction.manager:
        all_orders = Order.query().all()
        logger.info('Will process {0} orders'.format(len(all_orders)))
        for idx, order in enumerate(all_orders):
            # History
            order._update_dates_from_history()

    logger.info('Finished processing {0} orders'.format(len(all_orders)))


if __name__ == '__main__':
    main()
