"""Add indices to slug.

Revision ID: c2cfcd041763
Revises: 0c66e448825d
Create Date: 2016-12-13 13:38:02.287940
"""
from alembic import op

revision = 'c2cfcd041763'
down_revision = '0c66e448825d'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.create_index(op.f('ix_assets_slug'), 'assets', ['slug'], unique=False)
    op.create_index(op.f('ix_assets_version_slug'), 'assets_version', ['slug'], unique=False)
    op.create_index(op.f('ix_customercontacts_slug'), 'customercontacts', ['slug'], unique=False)
    op.create_index(op.f('ix_customers_slug'), 'customers', ['slug'], unique=False)
    op.create_index(op.f('ix_customers_version_slug'), 'customers_version', ['slug'], unique=False)
    op.create_index(op.f('ix_jobs_slug'), 'jobs', ['slug'], unique=False)
    op.create_index(op.f('ix_jobs_version_slug'), 'jobs_version', ['slug'], unique=False)
    op.create_unique_constraint(None, 'localroles', ['id'])
    op.create_index(op.f('ix_professionals_slug'), 'professionals', ['slug'], unique=False)
    op.create_index(op.f('ix_professionals_version_slug'), 'professionals_version', ['slug'],
                    unique=False)
    op.create_index(op.f('ix_projects_slug'), 'projects', ['slug'], unique=False)
    op.create_index(op.f('ix_projects_version_slug'), 'projects_version', ['slug'], unique=False)


def downgrade():
    """Downgrade database model."""
    op.drop_index(op.f('ix_projects_version_slug'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_slug'), table_name='projects')
    op.drop_index(op.f('ix_professionals_version_slug'), table_name='professionals_version')
    op.drop_index(op.f('ix_professionals_slug'), table_name='professionals')
    op.drop_constraint(None, 'localroles', type_='unique')
    op.drop_index(op.f('ix_jobs_version_slug'), table_name='jobs_version')
    op.drop_index(op.f('ix_jobs_slug'), table_name='jobs')
    op.drop_index(op.f('ix_customers_version_slug'), table_name='customers_version')
    op.drop_index(op.f('ix_customers_slug'), table_name='customers')
    op.drop_index(op.f('ix_customercontacts_slug'), table_name='customercontacts')
    op.drop_index(op.f('ix_assets_version_slug'), table_name='assets_version')
    op.drop_index(op.f('ix_assets_slug'), table_name='assets')
