"""LEICA-37-Add uploaded by field.

Revision ID: fd5b6154286b
Revises: dc7971325d41
Create Date: 2016-09-23 17:05:55.212714
"""
from alembic import op

import sqlalchemy as sa
import sqlalchemy_utils

revision = 'fd5b6154286b'
down_revision = 'dc7971325d41'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.add_column(
        'assets',
        sa.Column('uploaded_by',
                  sqlalchemy_utils.types.uuid.UUIDType(),
                  nullable=False)
    )


def downgrade():
    """Downgrade database model."""
    op.drop_column('assets', 'uploaded_by')
