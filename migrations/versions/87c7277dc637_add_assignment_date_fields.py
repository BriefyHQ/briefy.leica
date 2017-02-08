"""Add Assignment date fields.

Revision ID: 87c7277dc637
Revises: c4aa95bfb0a2
Create Date: 2017-02-08 21:05:49.431570
"""
from alembic import op
from briefy.common.db.types.aware_datetime import AwareDateTime

import sqlalchemy as sa

revision = '87c7277dc637'
down_revision = 'c4aa95bfb0a2'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.add_column('assignments', sa.Column('assignment_date', AwareDateTime(), nullable=True))
    op.add_column('assignments', sa.Column('last_approval_date', AwareDateTime(), nullable=True))
    op.add_column('assignments', sa.Column('last_submission_date', AwareDateTime(), nullable=True))
    op.add_column('assignments', sa.Column('submission_date', AwareDateTime(), nullable=True))
    op.create_index(op.f('ix_assignments_assignment_date'), 'assignments', ['assignment_date'],
                    unique=False)
    op.create_index(op.f('ix_assignments_last_approval_date'), 'assignments',
                    ['last_approval_date'], unique=False)
    op.create_index(op.f('ix_assignments_last_submission_date'), 'assignments',
                    ['last_submission_date'], unique=False)
    op.create_index(op.f('ix_assignments_scheduled_datetime'), 'assignments',
                    ['scheduled_datetime'], unique=False)
    op.create_index(op.f('ix_assignments_submission_date'), 'assignments', ['submission_date'],
                    unique=False)
    op.add_column('assignments_version',
                  sa.Column('assignment_date', AwareDateTime(), autoincrement=False, nullable=True))
    op.add_column('assignments_version',
                  sa.Column('last_approval_date', AwareDateTime(), autoincrement=False,
                            nullable=True))
    op.add_column('assignments_version',
                  sa.Column('last_submission_date', AwareDateTime(), autoincrement=False,
                            nullable=True))
    op.add_column('assignments_version',
                  sa.Column('submission_date', AwareDateTime(), autoincrement=False, nullable=True))
    op.create_index(op.f('ix_assignments_version_assignment_date'), 'assignments_version',
                    ['assignment_date'], unique=False)
    op.create_index(op.f('ix_assignments_version_last_approval_date'), 'assignments_version',
                    ['last_approval_date'], unique=False)
    op.create_index(op.f('ix_assignments_version_last_submission_date'), 'assignments_version',
                    ['last_submission_date'], unique=False)
    op.create_index(op.f('ix_assignments_version_scheduled_datetime'), 'assignments_version',
                    ['scheduled_datetime'], unique=False)
    op.create_index(op.f('ix_assignments_version_submission_date'), 'assignments_version',
                    ['submission_date'], unique=False)


def downgrade():
    """Downgrade database model."""
    op.drop_index(op.f('ix_assignments_version_submission_date'), table_name='assignments_version')
    op.drop_index(op.f('ix_assignments_version_scheduled_datetime'),
                  table_name='assignments_version')
    op.drop_index(op.f('ix_assignments_version_last_submission_date'),
                  table_name='assignments_version')
    op.drop_index(op.f('ix_assignments_version_last_approval_date'),
                  table_name='assignments_version')
    op.drop_index(op.f('ix_assignments_version_assignment_date'), table_name='assignments_version')
    op.drop_column('assignments_version', 'submission_date')
    op.drop_column('assignments_version', 'last_submission_date')
    op.drop_column('assignments_version', 'last_approval_date')
    op.drop_column('assignments_version', 'assignment_date')
    op.drop_index(op.f('ix_assignments_submission_date'), table_name='assignments')
    op.drop_index(op.f('ix_assignments_scheduled_datetime'), table_name='assignments')
    op.drop_index(op.f('ix_assignments_last_submission_date'), table_name='assignments')
    op.drop_index(op.f('ix_assignments_last_approval_date'), table_name='assignments')
    op.drop_index(op.f('ix_assignments_assignment_date'), table_name='assignments')
    op.drop_column('assignments', 'submission_date')
    op.drop_column('assignments', 'last_submission_date')
    op.drop_column('assignments', 'last_approval_date')
    op.drop_column('assignments', 'assignment_date')
