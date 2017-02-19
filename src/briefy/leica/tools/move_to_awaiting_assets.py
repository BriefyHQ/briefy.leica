"""Move Assignments to awaiting assets."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.leica import logger
from briefy.leica.db import Session
from briefy.leica.models import Assignment
from briefy.leica.sync import db

import transaction


def main(session):
    """Move Assignments from scheduled to awaiting_assets."""
    now = datetime_utcnow()

    assignments = session.query(Assignment).filter(
        Assignment.scheduled_datetime < now,
        Assignment.state == 'scheduled'
    ).all()
    msg = 'Total assignments to be moved: {size}'
    msg = msg.format(size=len(assignments))
    print(msg)
    logger.info(msg)

    for assignment in assignments:
        wf = assignment.workflow
        wf.context = SystemUser
        wf.ready_for_upload()
        msg = 'Assignment {id} moved to awaiting_assets. Shoot time: {shoot_time}'
        msg = msg.format(id=assignment.id, shoot_time=assignment.scheduled_datetime)
        print(msg)
        logger.info(msg)

    transaction.commit()


if __name__ == '__main__':
    session = db.configure(Session)
    main(session)
