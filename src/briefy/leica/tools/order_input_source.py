"""Re-synch Order's input source (source attribute) from Knack."""

from briefy.leica.db import Session
from briefy.leica.models import Order
from briefy.leica.sync.db import configure
from briefy.leica.vocabularies import OrderInputSource as Source
from logging import getLogger

import briefy.knack as K
import transaction


def init():
    """Preread all values from the databases."""
    global logger, Job, jobs, orders, jobs_id
    logger = getLogger(__name__)
    Job = K.get_model("Job")
    jobs = Job.query.all()
    orders = Order.query().all()
    jobs_id = {j.id: j for j in jobs}


def is_briefy(kjob):
    """Check whether a Job object from Knack has briefy or custommer as input_source."""
    return "briefy" in str(kjob.input_source).lower()


def make_changes():
    """Where the magic happens."""
    changed_count = 0
    ignored_count = 0
    unchanged_count = 0
    for order in orders:
        if not order.external_id:
            ignored_count += 1
            continue
        if order.external_id not in jobs_id:
            ignored_count += 1
            logger.warn('Could not find order {0} on Knack records'.format(order.slug))
        kjob = jobs_id[order.external_id]
        new_source = Source.briefy if is_briefy(kjob) else Source.customer
        if order.source != new_source:
            changed_count += 1
            order.source = new_source
            session.add(order)
        else:
            unchanged_count += 1

    return changed_count, unchanged_count, ignored_count


def main():
    """Coordinate everything."""
    init()
    with transaction.manager:
        changed, unchanged, ignored = make_changes()
    print('changed: {0}, unchanged: {1}, ignored: {2} order input sources'.format(
        changed, unchanged, ignored
    ))


if __name__ == '__main__':
    session = configure(Session)
    main()
