"""initial version.

Revision ID: c59042edc459
Revises: 
Create Date: 2016-09-15 19:59:33.907591
"""
from alembic import op
from briefy.leica.models import types

import briefy.common
import sqlalchemy as sa
import sqlalchemy_utils

revision = 'c59042edc459'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.create_table('comments',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('comment_order', sa.Integer(), nullable=True),
    sa.Column('author_id', sqlalchemy_utils.types.uuid.UUIDType, nullable=False),
    sa.Column('in_reply_to', sqlalchemy_utils.types.uuid.UUIDType, nullable=True),
    sa.Column('entity_type', sa.String(length=255), nullable=True),
    sa.Column('entity_id', sqlalchemy_utils.types.uuid.UUIDType, nullable=True),
    sa.ForeignKeyConstraint(['in_reply_to'], ['comments.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('projects',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('briefing', sa.Text(), nullable=True),
    sa.Column('company_id', sqlalchemy_utils.types.uuid.UUIDType, nullable=False),
    sa.Column('currency_set_price', sqlalchemy_utils.types.currency.CurrencyType(length=3), nullable=True),
    sa.Column('abstract', sa.Text(), nullable=True),
    sa.Column('manager', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('set_price', sa.Integer(), nullable=False),
    sa.Column('release_template', sqlalchemy_utils.types.url.URLType(), nullable=True),
    sa.Column('req_iso', sa.String(), nullable=True),
    sa.Column('req_aperture', sa.String(), nullable=True),
    sa.Column('req_aspect_ratio', sa.String(), nullable=True),
    sa.Column('req_resolution', sa.Integer(), nullable=True),
    sa.Column('req_size', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('jobs',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('internal_job_id', sa.String(), nullable=False),
    sa.Column('customer_job_id', sa.String(), nullable=True),
    sa.Column('availability_1', sa.DateTime(), nullable=True),
    sa.Column('availability_2', sa.DateTime(), nullable=True),
    sa.Column('category', sqlalchemy_utils.types.choice.ChoiceType(types.CategoryChoices), nullable=True),
    sa.Column('client_delivery_link', sqlalchemy_utils.types.url.URLType(), nullable=True),
    sa.Column('client_feedback', sa.Text(), nullable=True),
    sa.Column('client_job_status', sqlalchemy_utils.types.choice.ChoiceType(types.ClientJobStatusChoices), nullable=True),
    sa.Column('client_specific_requirement', sa.Text(), nullable=True),
    sa.Column('company_id', sqlalchemy_utils.types.uuid.UUIDType, nullable=True),
    sa.Column('contact_person_id', sqlalchemy_utils.types.uuid.UUIDType, nullable=True),
    sa.Column('currency_payout', sqlalchemy_utils.types.currency.CurrencyType(length=3), nullable=True),
    sa.Column('finance_manager', sqlalchemy_utils.types.uuid.UUIDType, nullable=True),
    sa.Column('finance_manager_to_payout', sqlalchemy_utils.types.uuid.UUIDType, nullable=True),
    sa.Column('invoice_date', sa.DateTime(), nullable=True),
    sa.Column('payout_date', sa.DateTime(), nullable=True),
    sa.Column('photo_submission_link', sqlalchemy_utils.types.url.URLType(), nullable=True),
    sa.Column('photographer_payout', sa.Integer(), nullable=True),
    sa.Column('photographers_comment', sa.Text(), nullable=True),
    sa.Column('project_id', sqlalchemy_utils.types.uuid.UUIDType, nullable=False),
    sa.Column('project_manager_comment', sa.Text(), nullable=True),
    sa.Column('qa_manager', sqlalchemy_utils.types.uuid.UUIDType, nullable=True),
    sa.Column('quality_assurance_feedback', sa.Text(), nullable=True),
    sa.Column('responsible_photographer', sqlalchemy_utils.types.uuid.UUIDType, nullable=True),
    sa.Column('scheduled_shoot_date_time', sa.DateTime(), nullable=True),
    sa.Column('scheduling_issues', sqlalchemy_utils.types.choice.ChoiceType(types.SchedulingIssuesChoices), nullable=True),
    sa.Column('scouting_manager', sqlalchemy_utils.types.uuid.UUIDType, nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('signed_releases_contract', sqlalchemy_utils.types.uuid.UUIDType, nullable=True),
    sa.Column('travel_expenses', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('assets',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType, nullable=False),
    sa.Column('source_path', sa.String(length=1000), nullable=False),
    sa.Column('filename', sa.String(length=1000), nullable=False),
    sa.Column('content_type', sa.String(length=100), nullable=False),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('width', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('raw_metadata', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('owner', sa.String(length=255), nullable=False),
    sa.Column('author_id', sqlalchemy_utils.types.uuid.UUIDType, nullable=False),
    sa.Column('job_id', sqlalchemy_utils.types.uuid.UUIDType, nullable=False),
    sa.Column('history', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('job_locations',
    sa.Column('locality', sa.String(length=255), nullable=False),
    sa.Column('info', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('country', sqlalchemy_utils.types.country.CountryType(length=2), nullable=False),
    sa.Column('coordinates', briefy.common.db.types.geo.POINT(), nullable=True),
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('job_id', sqlalchemy_utils.types.uuid.UUIDType, nullable=False),
    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    """Downgrade database model."""
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('job_locations')
    op.drop_table('assets')
    op.drop_table('jobs')
    op.drop_table('projects')
    op.drop_table('comments')
    ### end Alembic commands ###
