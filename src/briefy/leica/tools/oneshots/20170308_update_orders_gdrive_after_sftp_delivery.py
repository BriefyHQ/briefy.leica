"""Update gdrive link on Agoda orders that do not have the gdrive info."""
from briefy.leica.models import Order
from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from urllib.parse import urlparse

import csv
import transaction

FNAME = 'src/briefy/leica/tools/oneshots/data/history_delivery_sftp_agoda.txt'


def main():
    """Update gdrive client delivery link in """
    infile = open(FNAME, 'r')
    reader = csv.DictReader(infile, delimiter='\t')
    for item in reader:
        customer_order_id = item.get('customer_id')
        order = Order.query().filter_by(customer_order_id=customer_order_id).one()
        delivery = order.delivery
        gdrive = delivery.get('gdrive') if delivery else None
        slack_gdrive = item.get('delivery')
        id_gdrive = urlparse(gdrive).path.split('/')[-1]
        id_slack_gdrive = urlparse(slack_gdrive).path.split('/')[-1]
        if not gdrive:
            delivery = delivery.copy()
            delivery['gdrive'] = slack_gdrive
            order.delivery = delivery
        elif id_gdrive != id_slack_gdrive:
            print('{0}\t{1}\t{2}\t{3}'.format(order.slug, order.title, gdrive, slack_gdrive))
        else:
            pass


if __name__ == '__main__':
    configure(Session)
    with transaction.manager:
        main()
