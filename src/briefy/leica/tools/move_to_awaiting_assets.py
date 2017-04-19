"""Move Assignments to awaiting assets."""
from briefy.leica.db import Session
from briefy.leica.sync import db
from briefy.leica.tasks.assignment import move_assignments_awaiting_assets

import transaction


if __name__ == '__main__':
    db.configure(Session)
    with transaction.manager:
        move_assignments_awaiting_assets()
