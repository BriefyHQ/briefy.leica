"""Export all Orders and transitions to a tsv file."""
from briefy.leica.db import Session
from briefy.leica.models import Order
from briefy.leica.models import UserProfile
from briefy.leica.sync import db
from dateutil.parser import parse

import csv


OUT_FNAME = '/tmp/orders_transitions.txt'
FIELDNAMES = (
    'uid',
    'id',
    'actor',
    'date',
    'state_from',
    'state_to',
    'transition_name',
    'message'
)


def main():
    """Get all orders from the database and export as tsv file."""
    all_orders = Order.query().all()
    total = len(all_orders)
    with open(OUT_FNAME, 'w') as fout:
        writer = csv.DictWriter(fout, fieldnames=FIELDNAMES, delimiter='\t')
        writer.writeheader()
        for i, order in enumerate(all_orders):
            for history in order.state_history:
                actor = history.get('actor')
                try:
                    profile = UserProfile.get(actor)
                except Exception:
                    fullname = actor.get('fullname')
                else:
                    if not profile and actor == 'be319e15-d256-4587-a871-c3476affa309':
                        fullname = 'SystemUser'
                    else:
                        fullname = profile.fullname if profile else actor

                item = dict(
                    uid=order.id,
                    id=order.slug,
                    actor=fullname,
                    date=parse(history.get('date')).strftime('%Y-%m-%d %H:%M:%S'),
                    state_from=history.get('from'),
                    state_to=history.get('to'),
                    transition_name=history.get('transition'),
                    message=history.get('message')
                )
                writer.writerow(item)
            print('State history exported for Order {item} of {total}. Slug: {slug}'.format(
                slug=order.slug,
                item=i,
                total=total
            ))


if __name__ == '__main__':
    db.configure(Session)
    main()
