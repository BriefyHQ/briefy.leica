"""AddShootingDate.

Revision ID: d680cc897210
Revises: e732b832d74b
Create Date: 2016-10-19 16:49:50.286530
"""
from alembic import op


import briefy.common
import sqlalchemy as sa
import sqlalchemy_utils

revision = 'd680cc897210'
down_revision = 'e732b832d74b'
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
    op.add_column('jobs', sa.Column(
        'scheduled_datetime',
        briefy.common.db.types.aware_datetime.AwareDateTime(), nullable=True)
    )


def downgrade():
    """Downgrade database model."""
    op.drop_column('jobs', 'scheduled_datetime')
