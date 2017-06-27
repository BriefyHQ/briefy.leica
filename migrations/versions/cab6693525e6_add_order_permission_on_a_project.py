"""Add order permission on a project.

Revision ID: cab6693525e6
Revises: 6ba7b0b3c229
Create Date: 2017-06-27 12:10:44.926019
"""
from alembic import op
from sqlalchemy.dialects import postgresql

import sqlalchemy as sa

revision = 'cab6693525e6'
down_revision = '6ba7b0b3c229'
branch_labels = None
depends_on = None

UPDATES = '''
UPDATE projects SET add_order_roles='["g:customers", "g:briefy_pm"]';
'''


def data_upgrade():
    """Update data."""
    print(revision)
    # Update existing Orders and LeadOrders
    op.execute(UPDATES)



def upgrade():
    """Upgrade database model."""
    op.add_column(
        'projects',
        sa.Column('add_order_roles', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column(
        'projects_version',
        sa.Column(
            'add_order_roles',
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True
        )
    )
    data_upgrade()


def downgrade():
    """Downgrade database model."""
    op.drop_column('projects_version', 'add_order_roles')
    op.drop_column('projects', 'add_order_roles')
