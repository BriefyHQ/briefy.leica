"""Update Assignment and Order Asset types field to the value in the Project.."""
from briefy.leica.db import Session
from briefy.leica.models import Order
from briefy.leica.models import Project
from briefy.leica.sync import db

import transaction


def main(session):
    """Update Orders and Assignment asset types value."""
    project_values = {project.id: project.asset_types
                      for project in Project.query().all()}
    for i, order_id in enumerate(session.query(Order.id)):
        order = Order.get(order_id)
        value = project_values.get(order.project_id)
        setattr(order, 'asset_types', value)
        for assignment in order.assignments:
            setattr(assignment, 'asset_types', value)

        print('{0} - Order and Assignments asset_types updated: {1}'.format(i, order.id))

        if i % 10 == 0:
            transaction.commit()


if __name__ == '__main__':
    session = db.configure(Session)
    with transaction.manager:
        main(session)
