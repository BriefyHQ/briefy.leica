"""Database Refactor.

Revision ID: 4ab62c901d68
Revises:
Create Date: 2016-12-02 17:06:18.985479
"""
from alembic import op
from briefy.common.db.types.aware_datetime import AwareDateTime
from briefy.common.vocabularies.person import GenderCategories
from briefy.common.db.types.geo import POINT
from briefy.leica.models.professional.location import DistanceUnits
from briefy.leica.vocabularies import JobInputSource
from briefy.common.vocabularies.categories import CategoryChoices
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.timezone import TimezoneType
from sqlalchemy_utils.types.uuid import UUIDType

import sqlalchemy as sa
import sqlalchemy_utils

revision = '4ab62c901d68'
down_revision = None
branch_labels = None
depends_on = None

# Monkey patch calls for which alembic create bogus parameters:

original_uuid_type = UUIDType


def monkey_uuid_type(*args, length=None, **kw):
    return original_uuid_type(*args, **kw)


UUIDType = monkey_uuid_type

original_timezone_type = TimezoneType


def monkey_timezone_type(*args, length=None, **kw):
    return original_timezone_type(*args, **kw)


TimezoneType = monkey_timezone_type


def upgrade():
    """Upgrade database model."""
    op.create_table(
        'assets_version',
        sa.Column('source_path', sa.String(length=1000), autoincrement=False,
                  nullable=True),
        sa.Column('filename', sa.String(length=1000), autoincrement=False,
                  nullable=True),
        sa.Column('content_type', sa.String(length=100), autoincrement=False,
                  nullable=True),
        sa.Column('size', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('width', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('height', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('raw_metadata', JSONType(),
                  autoincrement=False, nullable=True),
        sa.Column('id', UUIDType(length=16), autoincrement=False, nullable=False),
        sa.Column('title', sa.String(), autoincrement=False, nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('type', sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column('owner', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('professional_id', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('uploaded_by', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('job_id', UUIDType(length=16), autoincrement=False, nullable=True),
        sa.Column('history', JSONType(),
                  autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False,
                  nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_assets_version_end_transaction_id'), 'assets_version',
        ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_assets_version_operation_type'), 'assets_version', ['operation_type'],
        unique=False)
    op.create_index(
        op.f('ix_assets_version_transaction_id'), 'assets_version', ['transaction_id'],
        unique=False)
    op.create_table(
        'comments',
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', JSONType(),
                  nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('comment_order', sa.Integer(), nullable=True),
        sa.Column('author_id', UUIDType(length=16), nullable=False),
        sa.Column('in_reply_to', UUIDType(length=16), nullable=True),
        sa.Column('entity_type', sa.String(length=255), nullable=True),
        sa.Column('entity_id', UUIDType(length=16), nullable=True),
        sa.ForeignKeyConstraint(['in_reply_to'], ['comments.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_table(
        'customers',
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', JSONType(),
                  nullable=True),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_table(
        'customers_version',
        sa.Column('id', UUIDType(length=16), autoincrement=False, nullable=False),
        sa.Column('title', sa.String(), autoincrement=False, nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('external_id', sa.String(), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False,
                  nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_customers_version_end_transaction_id'), 'customers_version',
        ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_customers_version_operation_type'), 'customers_version',
        ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_customers_version_transaction_id'), 'customers_version',
        ['transaction_id'], unique=False)
    op.create_table(
        'images_version',
        sa.Column('id', UUIDType(length=16), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False,
                  nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_images_version_end_transaction_id'), 'images_version',
        ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_images_version_operation_type'), 'images_version', ['operation_type'],
        unique=False)
    op.create_index(
        op.f('ix_images_version_transaction_id'), 'images_version', ['transaction_id'],
        unique=False)
    op.create_table(
        'jobs_version',
        sa.Column('external_id', sa.String(), autoincrement=False, nullable=True),
        sa.Column('id', UUIDType(length=16), autoincrement=False, nullable=False),
        sa.Column('title', sa.String(), autoincrement=False, nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('project_manager', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('finance_manager', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('scout_manager', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('qa_manager', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('payout_currency',
                  sqlalchemy_utils.types.currency.CurrencyType(length=3),
                  autoincrement=False, nullable=True),
        sa.Column('payout_value', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('travel_expenses', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('additional_compensation', sa.Integer(), autoincrement=False,
                  nullable=True),
        sa.Column('price_currency',
                  sqlalchemy_utils.types.currency.CurrencyType(length=3),
                  autoincrement=False, nullable=True),
        sa.Column('price', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('availability', JSONType(),
                  autoincrement=False, nullable=True),
        sa.Column('scheduled_datetime', AwareDateTime(), autoincrement=False,
                  nullable=True),
        sa.Column('customer_id', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('project_id', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('professional_id', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('requirements', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('number_of_assets', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('category', ChoiceType(CategoryChoices, impl=sa.String()), nullable=True),
        sa.Column('source', ChoiceType(JobInputSource, impl=sa.String()), nullable=True),
        sa.Column('job_id', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('customer_job_id', sa.String(), autoincrement=False, nullable=True),
        sa.Column('submission_path', sqlalchemy_utils.types.url.URLType(),
                  autoincrement=False, nullable=True),
        sa.Column('delivery', JSONType(),
                  autoincrement=False, nullable=True),
        sa.Column('total_assets', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('total_approvable_assets', sa.Integer(), autoincrement=False,
                  nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False,
                  nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_jobs_version_customer_job_id'), 'jobs_version', ['customer_job_id'],
        unique=False)
    op.create_index(
        op.f('ix_jobs_version_end_transaction_id'), 'jobs_version',
        ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_jobs_version_job_id'), 'jobs_version', ['job_id'], unique=False)
    op.create_index(
        op.f('ix_jobs_version_operation_type'), 'jobs_version', ['operation_type'],
        unique=False)
    op.create_index(
        op.f('ix_jobs_version_transaction_id'), 'jobs_version', ['transaction_id'],
        unique=False)
    op.create_table(
        'photographers_version',
        sa.Column('id', UUIDType(length=16), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False,
                  nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_photographers_version_end_transaction_id'), 'photographers_version',
        ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_photographers_version_operation_type'), 'photographers_version',
        ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_photographers_version_transaction_id'), 'photographers_version',
        ['transaction_id'], unique=False)
    op.create_table(
        'professionals',
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=False),
        sa.Column('last_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('gender', ChoiceType(GenderCategories, impl=sa.String()), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', JSONType(), nullable=True),
        sa.Column('internal', sa.Boolean(), nullable=True),
        sa.Column('partners', sa.Boolean(), nullable=True),
        sa.Column('main_email', sa.String(length=255), nullable=True),
        sa.Column('main_mobile', sa.String(length=255), nullable=True),
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.Column('photo_path', sa.String(length=255), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_table(
        'professionals_version',
        sa.Column('external_id', sa.String(), autoincrement=False, nullable=True),
        sa.Column('title', sa.String(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('first_name', sa.String(length=255), autoincrement=False,
                  nullable=True),
        sa.Column('last_name', sa.String(length=255), autoincrement=False,
                  nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('gender', ChoiceType(GenderCategories, impl=sa.String()),
                  autoincrement=False, nullable=True),
        sa.Column('birth_date', sa.Date(), autoincrement=False, nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('internal', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('partners', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('main_email', sa.String(length=255), autoincrement=False,
                  nullable=True),
        sa.Column('main_mobile', sa.String(length=255), autoincrement=False,
                  nullable=True),
        sa.Column('id', UUIDType(length=16), autoincrement=False, nullable=False),
        sa.Column('photo_path', sa.String(length=255), autoincrement=False,
                  nullable=True),
        sa.Column('type', sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False,
                  nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_professionals_version_end_transaction_id'), 'professionals_version',
        ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_professionals_version_operation_type'), 'professionals_version',
        ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_professionals_version_transaction_id'), 'professionals_version',
        ['transaction_id'], unique=False)
    op.create_table(
        'projects_version',
        sa.Column('external_id', sa.String(), autoincrement=False, nullable=True),
        sa.Column('id', UUIDType(length=16), autoincrement=False, nullable=False),
        sa.Column('title', sa.String(), autoincrement=False, nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('project_manager', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('finance_manager', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('scout_manager', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('qa_manager', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('customer_id', UUIDType(length=16), autoincrement=False,
                  nullable=True),
        sa.Column('tech_requirements', JSONType(),
                  autoincrement=False, nullable=True),
        sa.Column('total_jobs', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('briefing', sqlalchemy_utils.types.url.URLType(), autoincrement=False,
                  nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False,
                  nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_projects_version_end_transaction_id'), 'projects_version',
        ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_projects_version_operation_type'), 'projects_version',
        ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_projects_version_transaction_id'), 'projects_version',
        ['transaction_id'], unique=False)
    op.create_table(
        'threesixtyimages_version',
        sa.Column('id', UUIDType(length=16), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False,
                  nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_threesixtyimages_version_end_transaction_id'),
        'threesixtyimages_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_threesixtyimages_version_operation_type'), 'threesixtyimages_version',
        ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_threesixtyimages_version_transaction_id'), 'threesixtyimages_version',
        ['transaction_id'], unique=False)
    op.create_table(
        'transaction',
        sa.Column('issued_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('remote_addr', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'videographers_version',
        sa.Column('id', UUIDType(length=16), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False,
                  nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_videographers_version_end_transaction_id'), 'videographers_version',
        ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_videographers_version_operation_type'), 'videographers_version',
        ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_videographers_version_transaction_id'), 'videographers_version',
        ['transaction_id'], unique=False)
    op.create_table(
        'videos_version',
        sa.Column('duration', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('codecs', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('audio_channels', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('id', UUIDType(length=16), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False,
                  nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_videos_version_end_transaction_id'), 'videos_version',
        ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_videos_version_operation_type'), 'videos_version', ['operation_type'],
        unique=False)
    op.create_index(
        op.f('ix_videos_version_transaction_id'), 'videos_version', ['transaction_id'],
        unique=False)
    op.create_table(
        'links',
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', JSONType(),
                  nullable=True),
        sa.Column('professional_id', UUIDType(length=16), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('url', sqlalchemy_utils.types.url.URLType(), nullable=False),
        sa.Column('is_social', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_table(
        'photographers',
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'projects',
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('project_manager', UUIDType(length=16), nullable=True),
        sa.Column('finance_manager', UUIDType(length=16), nullable=True),
        sa.Column('scout_manager', UUIDType(length=16), nullable=True),
        sa.Column('qa_manager', UUIDType(length=16), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', JSONType(),
                  nullable=True),
        sa.Column('customer_id', UUIDType(length=16), nullable=False),
        sa.Column('tech_requirements', JSONType(),
                  nullable=True),
        sa.Column('total_jobs', sa.Integer(), nullable=True),
        sa.Column('briefing', sqlalchemy_utils.types.url.URLType(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_table(
        'videographers',
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'workinglocations',
        sa.Column('locality', sa.String(length=255), nullable=False),
        sa.Column('info', JSONType(), nullable=True),
        sa.Column('country', sqlalchemy_utils.types.country.CountryType(length=2),
                  nullable=False),
        sa.Column('coordinates', POINT(), nullable=True),
        sa.Column('timezone', TimezoneType(length=50),
                  nullable=True),
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', JSONType(),
                  nullable=True),
        sa.Column('professional_id', UUIDType(length=16), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('range', sa.Integer(), nullable=True),
        sa.Column('range_unit', ChoiceType(DistanceUnits, impl=sa.String(5)), nullable=True),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_table(
        'jobs',
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('project_manager', UUIDType(length=16), nullable=True),
        sa.Column('finance_manager', UUIDType(length=16), nullable=True),
        sa.Column('scout_manager', UUIDType(length=16), nullable=True),
        sa.Column('qa_manager', UUIDType(length=16), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', JSONType(),
                  nullable=True),
        sa.Column('payout_currency',
                  sqlalchemy_utils.types.currency.CurrencyType(length=3),
                  nullable=True),
        sa.Column('payout_value', sa.Integer(), nullable=False),
        sa.Column('travel_expenses', sa.Integer(), nullable=False),
        sa.Column('additional_compensation', sa.Integer(), nullable=False),
        sa.Column('price_currency',
                  sqlalchemy_utils.types.currency.CurrencyType(length=3),
                  nullable=True),
        sa.Column('price', sa.Integer(), nullable=True),
        sa.Column('availability', JSONType(),
                  nullable=True),
        sa.Column('scheduled_datetime', AwareDateTime(), nullable=True),
        sa.Column('customer_id', UUIDType(length=16), nullable=True),
        sa.Column('project_id', UUIDType(length=16), nullable=False),
        sa.Column('professional_id', UUIDType(length=16), nullable=True),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('number_of_assets', sa.Integer(), nullable=True),
        sa.Column('category', ChoiceType(CategoryChoices, impl=sa.String()), nullable=True),
        sa.Column('source', ChoiceType(JobInputSource, impl=sa.String()), nullable=True),
        sa.Column('job_id', sa.Integer(), nullable=True),
        sa.Column('customer_job_id', sa.String(), nullable=True),
        sa.Column('submission_path', sqlalchemy_utils.types.url.URLType(),
                  nullable=True),
        sa.Column('delivery', JSONType(), nullable=True),
        sa.Column('total_assets', sa.Integer(), nullable=True),
        sa.Column('total_approvable_assets', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(
        op.f('ix_jobs_customer_job_id'), 'jobs', ['customer_job_id'], unique=False)
    op.create_index(
        op.f('ix_jobs_job_id'), 'jobs', ['job_id'], unique=False)
    op.create_table(
        'assets',
        sa.Column('source_path', sa.String(length=1000), nullable=False),
        sa.Column('filename', sa.String(length=1000), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('size', sa.Integer(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('raw_metadata', JSONType(),
                  nullable=True),
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', JSONType(),
                  nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('owner', sa.String(length=255), nullable=False),
        sa.Column('professional_id', UUIDType(length=16), nullable=False),
        sa.Column('uploaded_by', UUIDType(length=16), nullable=False),
        sa.Column('job_id', UUIDType(length=16), nullable=False),
        sa.Column('history', JSONType(), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_table(
        'joblocations',
        sa.Column('locality', sa.String(length=255), nullable=False),
        sa.Column('info', JSONType(), nullable=True),
        sa.Column('country', sqlalchemy_utils.types.country.CountryType(length=2),
                  nullable=False),
        sa.Column('coordinates', POINT(), nullable=True),
        sa.Column('timezone', TimezoneType(length=50),
                  nullable=True),
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', JSONType(),
                  nullable=True),
        sa.Column('contact', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('mobile', sa.String(length=255), nullable=True),
        sa.Column('job_id', UUIDType(length=16), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_table(
        'images',
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['assets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'threesixtyimages',
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['assets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'videos',
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('codecs', sa.Text(), nullable=True),
        sa.Column('audio_channels', sa.Integer(), nullable=True),
        sa.Column('id', UUIDType(length=16), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['assets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    """Downgrade database model."""
    op.drop_table('videos')
    op.drop_table('threesixtyimages')
    op.drop_table('images')
    op.drop_table('joblocations')
    op.drop_table('assets')
    op.drop_index(op.f('ix_jobs_job_id'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_customer_job_id'), table_name='jobs')
    op.drop_table('jobs')
    op.drop_table('workinglocations')
    op.drop_table('videographers')
    op.drop_table('projects')
    op.drop_table('photographers')
    op.drop_table('links')
    op.drop_index(op.f('ix_videos_version_transaction_id'), table_name='videos_version')
    op.drop_index(op.f('ix_videos_version_operation_type'), table_name='videos_version')
    op.drop_index(op.f('ix_videos_version_end_transaction_id'), table_name='videos_version')
    op.drop_table('videos_version')
    op.drop_index(op.f('ix_videographers_version_transaction_id'),
                  table_name='videographers_version')
    op.drop_index(op.f('ix_videographers_version_operation_type'),
                  table_name='videographers_version')
    op.drop_index(op.f('ix_videographers_version_end_transaction_id'),
                  table_name='videographers_version')
    op.drop_table('videographers_version')
    op.drop_table('transaction')
    op.drop_index(op.f('ix_threesixtyimages_version_transaction_id'),
                  table_name='threesixtyimages_version')
    op.drop_index(op.f('ix_threesixtyimages_version_operation_type'),
                  table_name='threesixtyimages_version')
    op.drop_index(op.f('ix_threesixtyimages_version_end_transaction_id'),
                  table_name='threesixtyimages_version')
    op.drop_table('threesixtyimages_version')
    op.drop_index(op.f('ix_projects_version_transaction_id'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_operation_type'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_end_transaction_id'), table_name='projects_version')
    op.drop_table('projects_version')
    op.drop_index(op.f('ix_professionals_version_transaction_id'),
                  table_name='professionals_version')
    op.drop_index(op.f('ix_professionals_version_operation_type'),
                  table_name='professionals_version')
    op.drop_index(op.f('ix_professionals_version_end_transaction_id'),
                  table_name='professionals_version')
    op.drop_table('professionals_version')
    op.drop_table('professionals')
    op.drop_index(op.f('ix_photographers_version_transaction_id'),
                  table_name='photographers_version')
    op.drop_index(op.f('ix_photographers_version_operation_type'),
                  table_name='photographers_version')
    op.drop_index(op.f('ix_photographers_version_end_transaction_id'),
                  table_name='photographers_version')
    op.drop_table('photographers_version')
    op.drop_index(op.f('ix_jobs_version_transaction_id'), table_name='jobs_version')
    op.drop_index(op.f('ix_jobs_version_operation_type'), table_name='jobs_version')
    op.drop_index(op.f('ix_jobs_version_job_id'), table_name='jobs_version')
    op.drop_index(op.f('ix_jobs_version_end_transaction_id'), table_name='jobs_version')
    op.drop_index(op.f('ix_jobs_version_customer_job_id'), table_name='jobs_version')
    op.drop_table('jobs_version')
    op.drop_index(op.f('ix_images_version_transaction_id'), table_name='images_version')
    op.drop_index(op.f('ix_images_version_operation_type'), table_name='images_version')
    op.drop_index(op.f('ix_images_version_end_transaction_id'), table_name='images_version')
    op.drop_table('images_version')
    op.drop_index(op.f('ix_customers_version_transaction_id'), table_name='customers_version')
    op.drop_index(op.f('ix_customers_version_operation_type'), table_name='customers_version')
    op.drop_index(op.f('ix_customers_version_end_transaction_id'), table_name='customers_version')
    op.drop_table('customers_version')
    op.drop_table('customers')
    op.drop_table('comments')
    op.drop_index(op.f('ix_assets_version_transaction_id'), table_name='assets_version')
    op.drop_index(op.f('ix_assets_version_operation_type'), table_name='assets_version')
    op.drop_index(op.f('ix_assets_version_end_transaction_id'), table_name='assets_version')
    op.drop_table('assets_version')
