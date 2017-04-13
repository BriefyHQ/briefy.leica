"""New field to store the number of rejections.

Revision ID: 53ae41d53636
Revises: 3298804dcdb0
Create Date: 2017-04-13 17:18:25.421695
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '53ae41d53636'
down_revision = '3298804dcdb0'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.add_column('assignments', sa.Column('refused_times', sa.Integer(), nullable=True))
    op.add_column('assignments_version', sa.Column('refused_times', sa.Integer(), autoincrement=False, nullable=True))

    op.drop_index('ix_billing_infos_title', table_name='billing_infos')
    op.create_unique_constraint(None, 'billing_infos', ['id'])
    op.drop_index('ix_billing_infos_version_title', table_name='billing_infos_version')
    op.alter_column('comments', 'entity_type',
                    existing_type=sa.VARCHAR(length=255),
                    nullable=False)
    op.add_column('orders', sa.Column('refused_times', sa.Integer(), nullable=True))
    op.add_column('orders_version', sa.Column('refused_times', sa.Integer(), autoincrement=False, nullable=True))
    op.alter_column('orders', 'category',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('orders', 'customer_id',
                    existing_type=postgresql.UUID(),
                    nullable=False)
    op.create_unique_constraint(None, 'userprofiles', ['email'])


def downgrade():
    """Downgrade database model."""
    op.drop_constraint(None, 'userprofiles', type_='unique')
    op.drop_column('orders_version', 'refused_times')
    op.alter_column('orders', 'customer_id',
                    existing_type=postgresql.UUID(),
                    nullable=True)
    op.alter_column('orders', 'category',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.drop_column('orders', 'refused_times')
    op.alter_column('comments', 'entity_type',
                    existing_type=sa.VARCHAR(length=255),
                    nullable=True)
    op.create_index('ix_billing_infos_version_title', 'billing_infos_version', ['title'], unique=False)
    op.drop_constraint(None, 'billing_infos', type_='unique')
    op.create_index('ix_billing_infos_title', 'billing_infos', ['title'], unique=False)
    op.drop_column('assignments_version', 'refused_times')
    op.drop_column('assignments', 'refused_times')
