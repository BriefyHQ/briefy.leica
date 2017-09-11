"""package type and requirment items.

Revision ID: a45eec2a6f1e
Revises: c8aa72b4d1c9
Create Date: 2017-09-11 12:50:21.796054
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils import types

from briefy.leica.vocabularies import PackageTypeChoices

revision = 'a45eec2a6f1e'
down_revision = 'c8aa72b4d1c9'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    # new fields
    op.add_column('orders', sa.Column('requirement_items', postgresql.JSONB(astext_type=sa.Text()),
                                      nullable=True))
    op.add_column('orders_version',
                  sa.Column('requirement_items', postgresql.JSONB(astext_type=sa.Text()),
                            autoincrement=False, nullable=True))
    op.add_column('projects', sa.Column('package_type', types.ChoiceType(choices=PackageTypeChoices,
                                                                         impl=sa.String()),
                                        autoincrement=False, nullable=False,
                                        server_default='on-demand'))
    op.add_column('projects_version', sa.Column('package_type',
                                                types.ChoiceType(choices=PackageTypeChoices,
                                                                 impl=sa.String()),
                                                autoincrement=False, nullable=True))
    # drop columns since this is now computed on the fly
    op.drop_column('projects', 'total_orders')
    op.drop_column('projects', 'total_leadorders')
    op.drop_column('projects_version', 'total_orders')
    op.drop_column('projects_version', 'total_leadorders')


def downgrade():
    """Downgrade database model."""
    op.add_column('projects_version',
                  sa.Column('total_leadorders', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('projects_version',
                  sa.Column('total_orders', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('projects_version', 'package_type')
    op.add_column('projects',
                  sa.Column('total_leadorders', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('projects',
                  sa.Column('total_orders', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('projects', 'package_type')
    op.drop_column('orders_version', 'requirement_items')
    op.drop_column('orders', 'requirement_items')
