"""Remove is_social column from Link.

Revision ID: 85efcdff093d
Revises: 1eda9b540641
Create Date: 2016-12-23 15:58:26.847585
"""
from alembic import op

import sqlalchemy as sa

revision = '85efcdff093d'
down_revision = '1eda9b540641'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.drop_column('links', 'is_social')


def downgrade():
    """Downgrade database model."""
    op.add_column('links', sa.Column('is_social', sa.BOOLEAN(), autoincrement=False, nullable=True))
