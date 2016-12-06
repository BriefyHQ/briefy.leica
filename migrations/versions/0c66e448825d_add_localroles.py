"""Add LocalRoles.

Revision ID: 0c66e448825d
Revises: 488db43730a4
Create Date: 2016-12-06 15:37:58.327488
"""
from alembic import op
from briefy.common.db.types.aware_datetime import AwareDateTime
from briefy.common.vocabularies.roles import LocalRolesChoices
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy_utils.types.uuid import UUIDType
from sqlalchemy.dialects import postgresql

import sqlalchemy as sa

revision = '0c66e448825d'
down_revision = '488db43730a4'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.create_table(
        'localroles',
        sa.Column('id', UUIDType(), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('entity_type', sa.String(length=255), nullable=False),
        sa.Column('entity_id', UUIDType(), nullable=False),
        sa.Column('user_id', UUIDType(), nullable=False),
        sa.Column(
            'role_name',
            ChoiceType(LocalRolesChoices),
            nullable=False
        ),
        sa.Column('can_create', sa.Boolean(), nullable=False),
        sa.Column('can_delete', sa.Boolean(), nullable=False),
        sa.Column('can_edit', sa.Boolean(), nullable=False),
        sa.Column('can_list', sa.Boolean(), nullable=False),
        sa.Column('can_view', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_localroles_can_create'), 'localroles', ['can_create'], unique=False)
    op.create_index(op.f('ix_localroles_can_delete'), 'localroles', ['can_delete'], unique=False)
    op.create_index(op.f('ix_localroles_can_edit'), 'localroles', ['can_edit'], unique=False)
    op.create_index(op.f('ix_localroles_can_list'), 'localroles', ['can_list'], unique=False)
    op.create_index(op.f('ix_localroles_can_view'), 'localroles', ['can_view'], unique=False)
    op.create_index(op.f('ix_localroles_entity_id'), 'localroles', ['entity_id'], unique=False)
    op.create_index(op.f('ix_localroles_entity_type'), 'localroles', ['entity_type'], unique=False)
    op.create_index(op.f('ix_localroles_user_id'), 'localroles', ['user_id'], unique=False)
    op.drop_index('idx_customerbillingaddresses_coordinates', table_name='customerbillingaddresses')
    op.create_unique_constraint(None, 'jobassignments', ['id'])
    op.drop_column('jobs', 'project_manager')
    op.drop_column('jobs', 'finance_manager')
    op.drop_column('jobs', 'scout_manager')
    op.drop_column('jobs', 'qa_manager')
    op.drop_column('jobs_version', 'project_manager')
    op.drop_column('jobs_version', 'finance_manager')
    op.drop_column('jobs_version', 'scout_manager')
    op.drop_column('jobs_version', 'qa_manager')
    op.drop_column('projects', 'scout_manager')
    op.drop_column('projects', 'finance_manager')
    op.drop_column('projects', 'project_manager')
    op.drop_column('projects', 'qa_manager')
    op.drop_column('projects_version', 'scout_manager')
    op.drop_column('projects_version', 'finance_manager')
    op.drop_column('projects_version', 'project_manager')
    op.drop_column('projects_version', 'qa_manager')


def downgrade():
    """Downgrade database model."""
    op.add_column('projects_version',
                  sa.Column('qa_manager', postgresql.UUID(), autoincrement=False, nullable=True))
    op.add_column('projects_version',
                  sa.Column('project_manager', postgresql.UUID(), autoincrement=False,
                            nullable=True))
    op.add_column('projects_version',
                  sa.Column('finance_manager', postgresql.UUID(), autoincrement=False,
                            nullable=True))
    op.add_column('projects_version',
                  sa.Column('scout_manager', postgresql.UUID(), autoincrement=False, nullable=True))
    op.add_column('projects',
                  sa.Column('qa_manager', postgresql.UUID(), autoincrement=False, nullable=True))
    op.add_column('projects', sa.Column('project_manager', postgresql.UUID(), autoincrement=False,
                                        nullable=True))
    op.add_column('projects', sa.Column('finance_manager', postgresql.UUID(), autoincrement=False,
                                        nullable=True))
    op.add_column('projects',
                  sa.Column('scout_manager', postgresql.UUID(), autoincrement=False, nullable=True))
    op.add_column('jobs_version',
                  sa.Column('qa_manager', postgresql.UUID(), autoincrement=False, nullable=True))
    op.add_column('jobs_version',
                  sa.Column('scout_manager', postgresql.UUID(), autoincrement=False, nullable=True))
    op.add_column('jobs_version',
                  sa.Column('finance_manager', postgresql.UUID(), autoincrement=False,
                            nullable=True))
    op.add_column('jobs_version',
                  sa.Column('project_manager', postgresql.UUID(), autoincrement=False,
                            nullable=True))
    op.add_column('jobs',
                  sa.Column('qa_manager', postgresql.UUID(), autoincrement=False, nullable=True))
    op.add_column('jobs',
                  sa.Column('scout_manager', postgresql.UUID(), autoincrement=False, nullable=True))
    op.add_column('jobs', sa.Column('finance_manager', postgresql.UUID(), autoincrement=False,
                                    nullable=True))
    op.add_column('jobs', sa.Column('project_manager', postgresql.UUID(), autoincrement=False,
                                    nullable=True))
    op.drop_constraint(None, 'jobassignments', type_='unique')
    op.create_index('idx_customerbillingaddresses_coordinates', 'customerbillingaddresses',
                    ['coordinates'], unique=False)
    op.drop_index(op.f('ix_localroles_user_id'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_entity_type'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_entity_id'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_can_view'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_can_list'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_can_edit'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_can_delete'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_can_create'), table_name='localroles')
    op.drop_table('localroles')
