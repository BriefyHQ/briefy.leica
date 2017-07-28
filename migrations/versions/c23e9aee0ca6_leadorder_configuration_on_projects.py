"""LeadOrder configuration on Projects.

Revision ID: c23e9aee0ca6
Revises: e79add10df68
Create Date: 2017-07-27 14:31:41.286403
"""
from alembic import op
from sqlalchemy.dialects import postgresql

import sqlalchemy as sa


revision = 'c23e9aee0ca6'
down_revision = 'e79add10df68'
branch_labels = None
depends_on = None


UPDATE_LEADORDER_CONFIGURATION = """
UPDATE 
    PROJECTS
SET
    leadorder_confirmation_fields='["availability"]'
WHERE
    order_type='leadorder'
"""


def data_upgrade():
    """Update data."""
    op.execute(UPDATE_LEADORDER_CONFIGURATION)


def upgrade():
    """Upgrade database model."""
    op.add_column('projects', sa.Column('leadorder_confirmation_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('projects_version', sa.Column('leadorder_confirmation_fields', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
    data_upgrade()


def downgrade():
    """Downgrade database model."""
    op.drop_column('projects_version', 'leadorder_confirmation_fields')
    op.drop_column('projects', 'leadorder_confirmation_fields')
