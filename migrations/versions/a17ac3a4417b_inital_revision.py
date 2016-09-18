"""Inital revision.

Revision ID: a17ac3a4417b
Revises:
Create Date: 2016-09-18 20:35:17.984423
"""
from alembic import op
from briefy.leica.models import types

import briefy.common
import sqlalchemy as sa
import sqlalchemy_utils

revision = 'a17ac3a4417b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.create_table('comments',
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=False),
                    sa.Column('created_at', briefy.common.db.types.aware_datatime.AwareDateTime(),
                              nullable=True),
                    sa.Column('updated_at', briefy.common.db.types.aware_datatime.AwareDateTime(),
                              nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(),
                              nullable=True),
                    sa.Column('type', sa.String(length=50), nullable=True),
                    sa.Column('content', sa.Text(), nullable=False),
                    sa.Column('comment_order', sa.Integer(), nullable=True),
                    sa.Column('author_id', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=False),
                    sa.Column('in_reply_to', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=True),
                    sa.Column('entity_type', sa.String(length=255), nullable=True),
                    sa.Column('entity_id', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=True),
                    sa.ForeignKeyConstraint(['in_reply_to'], ['comments.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_table('customers',
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('slug', sa.String(length=255), nullable=True),
                    sa.Column('created_at', briefy.common.db.types.aware_datatime.AwareDateTime(),
                              nullable=True),
                    sa.Column('updated_at', briefy.common.db.types.aware_datatime.AwareDateTime(),
                              nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(),
                              nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_table('projects',
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('slug', sa.String(length=255), nullable=True),
                    sa.Column('project_manager', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=True),
                    sa.Column('finance_manager', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=True),
                    sa.Column('scout_manager', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=True),
                    sa.Column('qa_manager', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=True),
                    sa.Column('created_at', briefy.common.db.types.aware_datatime.AwareDateTime(),
                              nullable=True),
                    sa.Column('updated_at', briefy.common.db.types.aware_datatime.AwareDateTime(),
                              nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(),
                              nullable=True),
                    sa.Column('customer_id', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=False),
                    sa.Column('tech_requirements', sqlalchemy_utils.types.json.JSONType(),
                              nullable=True),
                    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_table('jobs',
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=False),
                    sa.Column('project_manager', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=True),
                    sa.Column('finance_manager', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=True),
                    sa.Column('scout_manager', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=True),
                    sa.Column('qa_manager', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=True),
                    sa.Column('created_at', briefy.common.db.types.aware_datatime.AwareDateTime(),
                              nullable=True),
                    sa.Column('updated_at', briefy.common.db.types.aware_datatime.AwareDateTime(),
                              nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(),
                              nullable=True),
                    sa.Column('project_id', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=False),
                    sa.Column('professional', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=True),
                    sa.Column('title', sa.String(length=255), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('job_requirements', sa.Text(), nullable=True),
                    sa.Column('category',
                              sqlalchemy_utils.types.choice.ChoiceType(types.CategoryChoices),
                              nullable=True),
                    sa.Column('job_id', sa.String(), nullable=False),
                    sa.Column('customer_job_id', sa.String(), nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_table('assets',
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=False),
                    sa.Column('source_path', sa.String(length=1000), nullable=False),
                    sa.Column('filename', sa.String(length=1000), nullable=False),
                    sa.Column('content_type', sa.String(length=100), nullable=False),
                    sa.Column('size', sa.Integer(), nullable=True),
                    sa.Column('width', sa.Integer(), nullable=True),
                    sa.Column('height', sa.Integer(), nullable=True),
                    sa.Column('raw_metadata', sqlalchemy_utils.types.json.JSONType(),
                              nullable=True),
                    sa.Column('created_at', briefy.common.db.types.aware_datatime.AwareDateTime(),
                              nullable=True),
                    sa.Column('updated_at', briefy.common.db.types.aware_datatime.AwareDateTime(),
                              nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(),
                              nullable=True),
                    sa.Column('title', sa.String(length=255), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.Column('owner', sa.String(length=255), nullable=False),
                    sa.Column('author_id', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=False),
                    sa.Column('job_id', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=False),
                    sa.Column('history', sqlalchemy_utils.types.json.JSONType(), nullable=True),
                    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_table('job_locations',
                    sa.Column('locality', sa.String(length=255), nullable=False),
                    sa.Column('info', sqlalchemy_utils.types.json.JSONType(), nullable=True),
                    sa.Column('country', sqlalchemy_utils.types.country.CountryType(length=2),
                              nullable=False),
                    sa.Column('coordinates', briefy.common.db.types.geo.POINT(), nullable=True),
                    sa.Column('timezone', sqlalchemy_utils.types.timezone.TimezoneType(),
                              nullable=True),
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=False),
                    sa.Column('created_at', briefy.common.db.types.aware_datatime.AwareDateTime(),
                              nullable=True),
                    sa.Column('updated_at', briefy.common.db.types.aware_datatime.AwareDateTime(),
                              nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(),
                              nullable=True),
                    sa.Column('job_id', sqlalchemy_utils.types.uuid.UUIDType,
                              nullable=False),
                    sa.Column('contact_information', sqlalchemy_utils.types.json.JSONType(),
                              nullable=True),
                    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )


def downgrade():
    """Downgrade database model."""
    op.drop_table('job_locations')
    op.drop_table('assets')
    op.drop_table('jobs')
    op.drop_table('projects')
    op.drop_table('customers')
    op.drop_table('comments')