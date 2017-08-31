"""Add total leadorders column on projects.

Revision ID: a7d84093cfcf
Revises: 90177ad0654d
Create Date: 2017-08-01 12:35:58.971396
"""
import sqlalchemy as sa
from alembic import op

revision = 'a7d84093cfcf'
down_revision = '90177ad0654d'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.add_column('projects', sa.Column('total_leadorders', sa.Integer(), nullable=True))
    op.add_column('projects_version',
                  sa.Column('total_leadorders', sa.Integer(), autoincrement=False, nullable=True))

    update_total_orders = """
    UPDATE projects set total_orders = source.total FROM
    (SELECT 
    count(distinct orders.id) as total,
    orders.project_id as project_id
    FROM orders WHERE orders.current_type = 'order'
    GROUP BY project_id
    ) as source
    WHERE projects.id = source.project_id;
    """
    op.execute(update_total_orders)

    update_total_leadorders = """
    UPDATE projects set total_leadorders = source.total FROM
    (SELECT 
    count(distinct orders.id) as total,
    orders.project_id as project_id
    FROM orders WHERE orders.current_type = 'leadorder'
    GROUP BY project_id
    ) as source
    WHERE projects.id = source.project_id;
    """
    op.execute(update_total_leadorders)


def downgrade():
    """Downgrade database model."""
    op.drop_index(op.f('ix_workinglocations_state'), table_name='workinglocations')
    op.drop_column('projects_version', 'total_leadorders')
    op.drop_column('projects', 'total_leadorders')
