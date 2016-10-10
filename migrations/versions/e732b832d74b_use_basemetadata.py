"""Use BaseMetadata.

Revision ID: e732b832d74b
Revises: 052369f28e4d
Create Date: 2016-10-10 13:45:34.894766
"""
from alembic import op

import sqlalchemy as sa
import sqlalchemy_utils

revision = 'e732b832d74b'
down_revision = '052369f28e4d'
branch_labels = None
depends_on = None


# Monkey patch calls for which alembic create bogus parameters:

original_uuid_type = sqlalchemy_utils.types.uuid.UUIDType


def monkey_uuid_type(*args, length=None,  **kw):
    return original_uuid_type(*args, **kw)
sqlalchemy_utils.types.uuid.UUIDType = monkey_uuid_type


original_timezone_type = sqlalchemy_utils.types.timezone.TimezoneType


def monkey_timezone_type(*args, length=None, **kw):
    return original_timezone_type(*args, **kw)
sqlalchemy_utils.types.timezone.TimezoneType = monkey_timezone_type


def upgrade():
    """Upgrade database model."""
    op.add_column('jobs', sa.Column('slug', sa.String(length=255), nullable=True))


def downgrade():
    """Downgrade database model."""
    op.drop_column('jobs', 'slug')
