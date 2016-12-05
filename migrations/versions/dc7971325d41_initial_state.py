"""initial_state.

Revision ID: dc7971325d41
Revises:
Create Date: 2016-09-21 19:13:13.512872
"""
from alembic import op
from briefy.leica.models import types

import briefy.common
import sqlalchemy as sa
import sqlalchemy_utils

revision = 'dc7971325d41'
down_revision = None
branch_labels = None
depends_on = None

# Money patch calls for which alembic create bogus parameters:

original_uuid_type = sqlalchemy_utils.types.uuid.UUIDType


def monkey_uuid_type(*args, length=None, **kw):
    return original_uuid_type(*args, **kw)


sqlalchemy_utils.types.uuid.UUIDType = monkey_uuid_type

original_timezone_type = sqlalchemy_utils.types.timezone.TimezoneType


def monkey_timezone_type(*args, length=None, **kw):
    return original_timezone_type(*args, **kw)


sqlalchemy_utils.types.timezone.TimezoneType = monkey_timezone_type


def upgrade():
    """Upgrade database model."""
    op.create_table('comments',
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=False),
                    sa.Column('created_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('updated_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history',
                              sqlalchemy_utils.types.json.JSONType(), nullable=True),
                    sa.Column('type', sa.String(length=50), nullable=True),
                    sa.Column('content', sa.Text(), nullable=False),
                    sa.Column('comment_order', sa.Integer(), nullable=True),
                    sa.Column('author_id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=False),
                    sa.Column('in_reply_to', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=True),
                    sa.Column('entity_type', sa.String(
                        length=255), nullable=True),
                    sa.Column('entity_id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['in_reply_to'], ['comments.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_table('customers',
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('slug', sa.String(length=255), nullable=True),
                    sa.Column('created_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('updated_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history',
                              sqlalchemy_utils.types.json.JSONType(), nullable=True),
                    sa.Column('external_id', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_table('professionals',
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('slug', sa.String(length=255), nullable=True),
                    sa.Column('created_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('updated_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history',
                              sqlalchemy_utils.types.json.JSONType(), nullable=True),
                    sa.Column('external_id', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_table('projects',
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('slug', sa.String(length=255), nullable=True),
                    sa.Column('project_manager', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=True),
                    sa.Column('finance_manager', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=True),
                    sa.Column('scout_manager', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=True),
                    sa.Column('qa_manager', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=True),
                    sa.Column('created_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('updated_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history',
                              sqlalchemy_utils.types.json.JSONType(), nullable=True),
                    sa.Column('customer_id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=False),
                    sa.Column('external_id', sa.String(), nullable=True),
                    sa.Column('tech_requirements',
                              sqlalchemy_utils.types.json.JSONType(), nullable=True),
                    sa.Column('brief', sa.String(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['customer_id'], ['customers.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_table('jobs',
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=False),
                    sa.Column('project_manager', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=True),
                    sa.Column('finance_manager', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=True),
                    sa.Column('scout_manager', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=True),
                    sa.Column('qa_manager', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=True),
                    sa.Column('created_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('updated_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history',
                              sqlalchemy_utils.types.json.JSONType(), nullable=True),
                    sa.Column('project_id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=False),
                    sa.Column('professional_id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=True),
                    sa.Column('title', sa.String(length=255), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('job_requirements', sa.Text(), nullable=True),
                    sa.Column(
                        'category',
                        sqlalchemy_utils.types.choice.ChoiceType(types.CategoryChoices),
                        nullable=True),
                    sa.Column('job_id', sa.String(), nullable=False),
                    sa.Column('customer_job_id', sa.String(), nullable=True),
                    sa.Column('number_of_photos', sa.Integer(), nullable=True),
                    sa.Column('_assignment_date',
                              briefy.common.db.types.aware_datetime.AwareDateTime(), nullable=True),
                    sa.Column('external_id', sa.String(), nullable=True),
                    sa.ForeignKeyConstraint(['professional_id'], [
                        'professionals.id'], ),
                    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_table('assets',
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=False),
                    sa.Column('source_path', sa.String(
                        length=1000), nullable=False),
                    sa.Column('filename', sa.String(
                        length=1000), nullable=False),
                    sa.Column('content_type', sa.String(
                        length=100), nullable=False),
                    sa.Column('size', sa.Integer(), nullable=True),
                    sa.Column('width', sa.Integer(), nullable=True),
                    sa.Column('height', sa.Integer(), nullable=True),
                    sa.Column('raw_metadata',
                              sqlalchemy_utils.types.json.JSONType(), nullable=True),
                    sa.Column('created_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('updated_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history',
                              sqlalchemy_utils.types.json.JSONType(), nullable=True),
                    sa.Column('title', sa.String(length=255), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.Column('owner', sa.String(length=255), nullable=False),
                    sa.Column('author_id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=False),
                    sa.Column('job_id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=False),
                    sa.Column('history', sqlalchemy_utils.types.json.JSONType(),
                              nullable=True),
                    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_table('job_locations',
                    sa.Column('locality', sa.String(
                        length=255), nullable=False),
                    sa.Column(
                        'info', sqlalchemy_utils.types.json.JSONType(), nullable=True),
                    sa.Column('country', sqlalchemy_utils.types.country.CountryType(
                        length=2), nullable=False),
                    sa.Column('coordinates', briefy.common.db.types.geo.POINT(),
                              nullable=True),
                    sa.Column('timezone', sqlalchemy_utils.types.timezone.TimezoneType(
                        length=50), nullable=True),
                    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=False),
                    sa.Column('created_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('updated_at', briefy.common.db.types.aware_datetime.AwareDateTime(
                    ), nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history',
                              sqlalchemy_utils.types.json.JSONType(), nullable=True),
                    sa.Column('job_id', sqlalchemy_utils.types.uuid.UUIDType(
                        length=16), nullable=False),
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
    op.drop_table('professionals')
    op.drop_table('customers')
    op.drop_table('comments')