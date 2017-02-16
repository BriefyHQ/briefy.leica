"""Add date and timezone fields to Order Assignment.

Revision ID: c1674bf2a6bb
Revises: 87c7277dc637
Create Date: 2017-02-16 18:43:41.270617
"""
from alembic import op
from briefy.common.db.types.aware_datetime import AwareDateTime
from sqlalchemy_utils import types

import sqlalchemy as sa

revision = 'c1674bf2a6bb'
down_revision = '87c7277dc637'
branch_labels = None
depends_on = None


def data_upgrade():
    """Update data."""

    # Timezone data on order
    op.execute(
        """update orders o
           set
             timezone = ol.timezone
           from
             orderlocations ol
           where
             o.id = ol.order_id;
        """
    )
    # Timezone data on assignment
    op.execute(
        """update assignments a
            set
              timezone = ol.timezone
            from
              orderlocations ol
            where
              a.order_id = ol.order_id;
        """
    )

    # Scheduled datetime update on order
    op.execute(
        """update orders o
            set
              scheduled_datetime = a.scheduled_datetime
            from
              assignments a
            where
              a.order_id = o.id and
              a.state not in ('cancelled', 'perm_reject')
        """
    )


def upgrade():
    """Upgrade database model."""
    op.add_column(
        'assignments', sa.Column('timezone', types.TimezoneType(), nullable=True)
    )
    op.add_column('orders', sa.Column('accept_date', AwareDateTime(), nullable=True))
    op.add_column('orders', sa.Column('deliver_date', AwareDateTime(), nullable=True))
    op.add_column('orders', sa.Column('last_deliver_date', AwareDateTime(), nullable=True))
    op.add_column('orders', sa.Column('scheduled_datetime', AwareDateTime(), nullable=True))
    op.add_column('orders', sa.Column('timezone', types.TimezoneType(), nullable=True))
    op.create_index(op.f('ix_orders_accept_date'), 'orders', ['accept_date'], unique=False)
    op.create_index(op.f('ix_orders_deliver_date'), 'orders', ['deliver_date'], unique=False)
    op.create_index(
        op.f('ix_orders_last_deliver_date'), 'orders', ['last_deliver_date'],
        unique=False
    )
    op.create_index(
        op.f('ix_orders_scheduled_datetime'), 'orders', ['scheduled_datetime'],
        unique=False
    )
    op.add_column(
        'orders_version',
        sa.Column('accept_date', AwareDateTime(), autoincrement=False, nullable=True)
    )
    op.add_column(
        'orders_version',
        sa.Column('deliver_date', AwareDateTime(), autoincrement=False, nullable=True)
    )
    op.add_column(
        'orders_version',
        sa.Column('last_deliver_date', AwareDateTime(), autoincrement=False, nullable=True)
    )
    op.create_index(
        op.f('ix_orders_version_accept_date'), 'orders_version', ['accept_date'], unique=False
    )
    op.create_index(
        op.f('ix_orders_version_deliver_date'), 'orders_version', ['deliver_date'], unique=False
    )
    op.create_index(
        op.f('ix_orders_version_last_deliver_date'), 'orders_version', ['last_deliver_date'],
        unique=False
    )
    data_upgrade()


def downgrade():
    """Downgrade database model."""
    op.drop_index(op.f('ix_orders_version_last_deliver_date'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_deliver_date'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_accept_date'), table_name='orders_version')
    op.drop_column('orders_version', 'last_deliver_date')
    op.drop_column('orders_version', 'deliver_date')
    op.drop_column('orders_version', 'accept_date')
    op.drop_index(op.f('ix_orders_scheduled_datetime'), table_name='orders')
    op.drop_index(op.f('ix_orders_last_deliver_date'), table_name='orders')
    op.drop_index(op.f('ix_orders_deliver_date'), table_name='orders')
    op.drop_index(op.f('ix_orders_accept_date'), table_name='orders')
    op.drop_column('orders', 'timezone')
    op.drop_column('orders', 'scheduled_datetime')
    op.drop_column('orders', 'last_deliver_date')
    op.drop_column('orders', 'deliver_date')
    op.drop_column('orders', 'accept_date')
    op.drop_column('assignments', 'timezone')

