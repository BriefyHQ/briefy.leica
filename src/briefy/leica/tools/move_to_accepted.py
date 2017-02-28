"""Move Order from delivered to accepted."""
from briefy.leica.tasks.order import move_order_accepted
from briefy.leica.db import Session
from briefy.leica.sync import db

import transaction


if __name__ == '__main__':
    db.configure(Session)
    with transaction.manager:
        move_order_accepted()
