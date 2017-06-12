"""Add Current Type to Order.

Revision ID: 6ba7b0b3c229
Revises: 9b54524b3970
Create Date: 2017-06-08 11:48:50.117020
"""
from alembic import op

import sqlalchemy as sa


revision = '6ba7b0b3c229'
down_revision = '9b54524b3970'
branch_labels = None
depends_on = None

UPDATES = '''
UPDATE orders SET type='order' where type is NULL;
UPDATE orders SET current_type='order' where type='order';
UPDATE orders SET current_type='leadorder' where type='leadorder';
UPDATE orders SET current_type='order' where type='leadorder' and state !='new';
'''


def data_upgrade():
    """Update data."""
    print(revision)
    # Update existing Orders and LeadOrders
    op.execute(UPDATES)


def upgrade():
    """Upgrade database model."""
    op.add_column('orders', sa.Column('current_type', sa.String(length=50), nullable=True))
    op.create_index(op.f('ix_orders_current_type'), 'orders', ['current_type'], unique=False)
    op.add_column(
        'orders_version',
        sa.Column('current_type', sa.String(length=50), autoincrement=False, nullable=True)
    )
    op.create_index(
        op.f('ix_orders_version_current_type'),
        'orders_version',
        ['current_type'],
        unique=False
    )
    data_upgrade()


def downgrade():
    """Downgrade database model."""
    op.drop_index(op.f('ix_orders_version_current_type'), table_name='orders_version')
    op.drop_column('orders_version', 'current_type')
    op.drop_index(op.f('ix_orders_current_type'), table_name='orders')
    op.drop_column('orders', 'current_type')
