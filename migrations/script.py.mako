"""${message}.

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""
from alembic import op
from briefy.leica.models import types
${imports if imports else ""}

import briefy.common
import sqlalchemy as sa
import sqlalchemy_utils

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


# Money patch calls for which alembic create bogus parameters:

original_uuid_type = sqlalchemy_utils.types.uuid.UUIDType
def monkey_uuid_type(*args,length=None,  **kw):
    return original_uuid_type(*args, **kw)
sqlalchemy_utils.types.uuid.UUIDType = monkey_uuid_type


original_timezone_type=sqlalchemy_utils.types.timezone.TimezoneType
def monkey_timezone_type(*args,length=None,  **kw):
    return original_timezone_type(*args, **kw)
sqlalchemy_utils.types.timezone.TimezoneType=monkey_timezone_type


def upgrade():
    """Upgrade database model."""
    ${upgrades if upgrades else "pass"}


def downgrade():
    """Downgrade database model."""
    ${downgrades if downgrades else "pass"}
