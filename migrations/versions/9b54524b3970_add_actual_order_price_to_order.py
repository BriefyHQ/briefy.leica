"""Add Actual Order Price to Order.

Revision ID: 9b54524b3970
Revises: 65a304bb948e
Create Date: 2017-05-28 14:19:57.931072
"""
from alembic import op

import sqlalchemy as sa

revision = '9b54524b3970'
down_revision = '65a304bb948e'
branch_labels = None
depends_on = None

UPDATES = '''
UPDATE PROJECTS SET price=12500 where id='6875b534-67ac-469d-979a-e5d7f4d147e5';
UPDATE PROJECTS SET price=100000 where id='ff9e8a4b-27ae-474f-94b5-148316ebd0c9';
UPDATE PROJECTS SET price=14000 where id='d53f54fe-580e-4ab1-8f0e-abda90eff210';
UPDATE PROJECTS SET price=16000 where id='92c4cf14-f4bf-4747-9661-3008d4210ad3';
UPDATE PROJECTS SET price=16000 where id='7348609b-23a3-43b2-a9c6-9db698c25cf7';
UPDATE PROJECTS SET price=37900 where id='445f0569-ddf5-4b18-860a-ff29db3d220a';
UPDATE
    ORDERS
SET
    price = temp1.price,
    actual_order_price = temp1.actual_order_price
from 
(select
   o.id as id,
   o.price as actual_order_price,
   p.price as price
from
   orders o,
   projects p
where
   p.id = o.project_id
)  as temp1
where
   orders.id = temp1.id;
'''


def data_upgrade():
    """Update data."""
    print(revision)
    # Update existing Orders
    op.execute(UPDATES)


def upgrade():
    """Upgrade database model."""
    op.add_column(
        'orders',
        sa.Column('actual_order_price', sa.Integer(), nullable=True)
    )
    op.add_column(
        'orders_version',
        sa.Column('actual_order_price', sa.Integer(), autoincrement=False, nullable=True)
    )
    data_upgrade()


def downgrade():
    """Downgrade database model."""
    op.drop_column('orders_version', 'actual_order_price')
    op.drop_column('orders', 'actual_order_price')
