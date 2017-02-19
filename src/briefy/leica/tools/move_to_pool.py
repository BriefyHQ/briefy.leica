"""Move Assignment to Pool."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.leica import logger
from briefy.leica.db import Session
from briefy.leica.sync import db
from briefy.leica.models import Order
from dateutil.parser import parse

import transaction


POOLS_CONFIG = (
    (
        'Delivery Hero Hamburg',
        '92032655-8c85-4480-a241-b3eb68d7d490',
        '51549a8e-918e-4cc3-ad21-ffd4ead0a74e'
    ),
    (
        'Delivery Hero Cologne',
        '04b71171-f032-452a-b31f-2ba179b2c360',
        '78246086-ae6d-424c-b77e-aa7a8cb81035'
    ),
    (
        'Delivery Hero Munich',
        '37e433e0-a472-417c-a236-0eec96f64376',
        '0e0dd21a-d948-4212-aaae-dedb5f8efb8d'
    ),
    (
        'Agoda Pattaya',
        '9d416e3f-39ce-4419-bb0a-d4d882f1fbf2',
        '6bc29461-8a6e-4d10-bd54-f48d498f7776'
    ),
    (
        'Agoda Phuket',
        'cddc09d1-cd92-4fde-be42-11e3cdd34e19',
        '4e7976d5-1a7f-4cfa-b6ba-08356bc7f162'
    ),
    (
        'Agoda Bangkok',
        '83b1f333-b270-43fd-8922-234bbdfaa855',
        '2edf1e7b-b7f0-4ca4-8d1b-9a8baf05662c'
    ),
    (
        'Agoda Bali',
        '009e2b7c-cc61-4f7b-ac34-7ced9a6bc0f5',
        '1dafb433-9431-4295-a349-92c4ad61c59e'
    ),
)


def main(session):
    """Move Assignments from scheduled to awaiting_assets."""
    for pool_name, pool_id, project_id in POOLS_CONFIG:
        orders = session.query(Order).filter(
            Order.state == 'received',
            Order.project_id == project_id
        ).all()

        for order in orders:
            now = datetime_utcnow()
            if order.availability:
                has_availability = False
                for date in order.availability:
                    date = parse(date)
                    date_diff = date - now
                    if date_diff.days >= 2:
                        has_availability = True

                assignment = order.assignment
                has_payout = assignment.payout_value and assignment.payout_currency
                print_msg = True

                if assignment.state != 'pending':
                    print_msg = False
                elif not has_availability:
                    msg = 'Assignment {id} has no availability two days in future.'
                elif assignment.pool_id:
                    msg = 'Assignment {id} is pending but already has a pool id.'
                elif not has_payout:
                    msg = 'Assignment {id} do not have payout information.'
                else:
                    wf = assignment.workflow
                    wf.context = SystemUser
                    fields = dict(pool_id=pool_id)
                    transition_message = 'Assignment published in Pool: {pool_name}'
                    transition_message = transition_message.format(pool_name=pool_name)
                    wf.publish(fields=fields, message=transition_message)
                    msg = 'Assignment {id} moved to published.'

                if print_msg:
                    msg = msg.format(id=assignment.id)
                    print(msg)
                    logger.info(msg)


if __name__ == '__main__':
    session = db.configure(Session)
    with transaction.manager:
        main(session)
