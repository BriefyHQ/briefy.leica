"""Disable professional relationship with jobs..

Revision ID: 052369f28e4d
Revises: 115dbdf4ca44
Create Date: 2016-10-04 22:32:14.787547
"""
from alembic import op
from briefy.leica.models import types

import briefy.common
import sqlalchemy as sa
import sqlalchemy_utils

revision = '052369f28e4d'
down_revision = '115dbdf4ca44'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.drop_constraint('jobs_professional_id_fkey', 'jobs', type_='foreignkey')


def downgrade():
    """Downgrade database model."""
    op.create_foreign_key('jobs_professional_id_fkey', 'jobs', 'professionals', ['professional_id'],
                          ['id'])
