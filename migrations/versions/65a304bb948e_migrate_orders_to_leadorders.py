"""Migrate orders to leadorders.

Revision ID: 65a304bb948e
Revises: decb04f1f444
Create Date: 2017-05-22 20:10:35.246087
"""
from alembic import op


revision = '65a304bb948e'
down_revision = 'decb04f1f444'
branch_labels = None
depends_on = None

INSERTS = '''INSERT INTO leadorders (id) SELECT id from orders where type = 'leadorder';'''
UPDATES = '''
UPDATE
    PROJECTS
SET
    order_type = 'leadorder'
WHERE
    id in (
        '0e0dd21a-d948-4212-aaae-dedb5f8efb8d',
        '51549a8e-918e-4cc3-ad21-ffd4ead0a74e',
        '78246086-ae6d-424c-b77e-aa7a8cb81035',
        '6bc29461-8a6e-4d10-bd54-f48d498f7776',
        '1dafb433-9431-4295-a349-92c4ad61c59e',
        '2edf1e7b-b7f0-4ca4-8d1b-9a8baf05662c',
        '4e7976d5-1a7f-4cfa-b6ba-08356bc7f162'
    );
UPDATE
    ORDERS
SET
    state = 'new',
    type = 'leadorder',
    state_history=array_to_json(
        array(
            select * from json_array_elements(temp1.state_history)
        ) || '{"transition": "remove_confirmation", "actor": "3966051e-6bfd-4998-9d96-432ddc93d8e9", "from": "received", "to": "new", "date": "2017-05-22T22:31:00+00:00", "message": "Automatic conversion of Order to Lead"}'::json
    )::json
from 
(
    SELECT id, state_history FROM ORDERS
    WHERE
        project_id in (
            '0e0dd21a-d948-4212-aaae-dedb5f8efb8d',
            '51549a8e-918e-4cc3-ad21-ffd4ead0a74e',
            '78246086-ae6d-424c-b77e-aa7a8cb81035',
            '6bc29461-8a6e-4d10-bd54-f48d498f7776',
            '1dafb433-9431-4295-a349-92c4ad61c59e',
            '2edf1e7b-b7f0-4ca4-8d1b-9a8baf05662c',
            '4e7976d5-1a7f-4cfa-b6ba-08356bc7f162'
        ) AND
        state in ('received') AND
        (
            json_typeof(availability) = 'null' OR
            (
                json_typeof(availability) = 'array' AND
                json_array_length(availability) = 0
            )
        ) AND
        json_array_length(state_history) < 4
) as temp1
where
   orders.id = temp1.id
'''  # noQA


def data_upgrade():
    """Update data."""
    print(revision)
    # Update existing Orders
    op.execute(UPDATES)
    # Create entries in LeadOrder table
    op.execute(INSERTS)


def upgrade():
    """Upgrade database model."""
    data_upgrade()


def downgrade():
    """Downgrade database model."""
    pass
