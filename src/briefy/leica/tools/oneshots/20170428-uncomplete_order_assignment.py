"""Undo Order accept and Assignment complete transitions."""

from briefy.leica.db import Session
from briefy.leica.models import Order
from briefy.leica.sync import db

import transaction


def remove_last_transition(item):
    """Remove the last transition and return the previous state."""
    state_histoy = item.state_history
    last_state = state_histoy[-1]['from']
    new_state_histoy = state_histoy[:-1]
    item.state_history = new_state_histoy
    item.state = last_state


def main(items):
    """Move back to last transition and state Order and last Assignment."""
    for slug in items:
        order = Order.query().filter_by(slug=slug).one()
        if order.state == 'completed':
            remove_last_transition(order)
            remove_last_transition(order.assignments[-1])
            if slug == '1701-PS9-679':
                order.delivery = None


if __name__ == '__main__':
    db.configure(Session)
    orders = [
        '1701-PS9-688',
        '1701-PS9-679'
    ]
    with transaction.manager:
        main(orders)
