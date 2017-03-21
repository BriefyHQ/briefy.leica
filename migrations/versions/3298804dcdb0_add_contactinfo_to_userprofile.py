"""Add ContactInfo to UserProfile.

Revision ID: 3298804dcdb0
Revises: 123d33102fe3
Create Date: 2017-03-21 19:21:24.213445
"""
from alembic import op
from sqlalchemy.dialects import postgresql

import sqlalchemy as sa

revision = '3298804dcdb0'
down_revision = '123d33102fe3'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.add_column(
        'userprofiles',
        sa.Column('messengers', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.create_unique_constraint(None, 'userprofiles', ['email'])
    op.add_column(
        'userprofiles_version',
        sa.Column(
            'messengers',
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False, nullable=True
        )
    )


def downgrade():
    """Downgrade database model."""
    op.drop_column('userprofiles_version', 'messengers')
    op.drop_column('userprofiles', 'messengers')
