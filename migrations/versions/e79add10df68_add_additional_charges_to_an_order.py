"""Add additional charges to an Order.

Revision ID: e79add10df68
Revises: cab6693525e6
Create Date: 2017-07-19 19:44:34.580333
"""
from alembic import op
from sqlalchemy.dialects import postgresql

import sqlalchemy as sa

revision = 'e79add10df68'
down_revision = 'cab6693525e6'
branch_labels = None
depends_on = None


UPDATES = '''
UPDATE
    ORDERS
SET
    total_order_price = temp1.actual_order_price
from  (SELECT id, actual_order_price FROM ORDERS) as temp1
where
   orders.id = temp1.id
'''  # noQA

def data_upgrade():
    """Update data."""
    print(revision)
    # Update existing Orders
    op.execute(UPDATES)


def upgrade():
    """Upgrade database model."""
    op.add_column(
        'orders',
        sa.Column('additional_charges', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column(
        'orders',
        sa.Column('total_order_price', sa.Integer(), nullable=True)
    )
    op.add_column(
        'orders_version',
        sa.Column('additional_charges', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column(
        'orders_version',
        sa.Column('total_order_price', sa.Integer(), nullable=True)
    )
    data_upgrade()


def downgrade():
    """Downgrade database model."""
    op.drop_column('orders_version', 'total_order_price')
    op.drop_column('orders_version', 'additional_charges')
    op.drop_column('orders', 'total_order_price')
    op.drop_column('orders', 'additional_charges')
