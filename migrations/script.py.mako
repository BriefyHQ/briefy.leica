"""${message}.

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""
from alembic import op
from briefy.common.db.types import geo
from briefy.common.db.types.aware_datetime import AwareDateTime
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.common.vocabularies.person import GenderCategories
from briefy.common.vocabularies.roles import LocalRolesChoices
from briefy.leica.vocabularies import OrderInputSource
from briefy.leica.vocabularies import TypesOfSetChoices
from briefy.leica.vocabularies import ContactTypes
from briefy.leica.models.professional.location import DistanceUnits
from sqlalchemy_utils import types
${imports if imports else ""}

import sqlalchemy as sa
import sqlalchemy_utils

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    """Upgrade database model."""
    ${upgrades if upgrades else "pass"}


def downgrade():
    """Downgrade database model."""
    ${downgrades if downgrades else "pass"}
