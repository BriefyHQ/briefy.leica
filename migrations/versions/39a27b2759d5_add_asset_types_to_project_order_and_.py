"""Add asset types to Project, Order and Assignment.

Revision ID: 39a27b2759d5
Revises: 53ae41d53636
Create Date: 2017-05-08 10:50:32.441780
"""
from alembic import op
from sqlalchemy.dialects import postgresql

import json
import sqlalchemy as sa

revision = '39a27b2759d5'
down_revision = '53ae41d53636'
branch_labels = None
depends_on = None

def data_upgrade():
    """Update data."""
    asset_types = ['Image']

    # Set projects with Image asset_type
    stmt = """
      UPDATE PROJECTS SET asset_types='{asset_types}' WHERE id != '{project_id}';
      UPDATE ORDERS SET asset_types='{asset_types}' WHERE project_id != '{project_id}';
      UPDATE ASSIGNMENTS SET asset_types='{asset_types}' WHERE id in (
        select 
            a.id
        from 
            assignments a,
            orders o
        where a.order_id = o.id and o.project_id !='{project_id}');
    """.format(
        asset_types=json.dumps(asset_types),
        project_id='331c05e8-b767-4d6a-7a48-7130414b5e2c'
    )  #  noQA
    op.execute(stmt)

    # Set projects with Matterport asset_type
    asset_types = ['Matterport']
    stmt = """
      UPDATE PROJECTS SET asset_types='{asset_types}' WHERE id = '{project_id}';
      UPDATE ORDERS SET asset_types='{asset_types}' WHERE project_id = '{project_id}';
      UPDATE ASSIGNMENTS SET asset_types='{asset_types}' WHERE id in (
        select 
            a.id
        from 
            assignments a,
            orders o
        where a.order_id = o.id and o.project_id ='{project_id}');
    """.format(
        asset_types=json.dumps(asset_types),
        project_id='331c05e8-b767-4d6a-7a48-7130414b5e2c'
    )  # noQA
    op.execute(stmt)


def upgrade():
    """Upgrade database model."""
    op.add_column(
        'assignments',
        sa.Column('asset_types', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column(
        'assignments_version',
        sa.Column(
            'asset_types',
            postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True)
    )
    op.add_column(
        'orders',
        sa.Column(
            'asset_types',
            postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column(
        'orders_version',
        sa.Column(
            'asset_types',
            postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True)
    )
    op.add_column(
        'projects',
        sa.Column(
            'asset_types',
            postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column(
        'projects_version',
        sa.Column(
            'asset_types',
            postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True)
    )
    data_upgrade()


def downgrade():
    """Downgrade database model."""
    op.drop_column('projects_version', 'asset_types')
    op.drop_column('projects', 'asset_types')
    op.drop_column('orders_version', 'asset_types')
    op.drop_column('orders', 'asset_types')
    op.drop_column('assignments_version', 'asset_types')
    op.drop_column('assignments', 'asset_types')
