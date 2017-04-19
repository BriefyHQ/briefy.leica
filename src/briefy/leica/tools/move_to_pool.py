"""Move Assignment to Pool."""
from briefy.leica.db import Session
from briefy.leica.sync import db
from briefy.leica.tasks.pool import move_assignments_to_pool

import transaction


if __name__ == '__main__':
    db.configure(Session)
    with transaction.manager:
        move_assignments_to_pool()
