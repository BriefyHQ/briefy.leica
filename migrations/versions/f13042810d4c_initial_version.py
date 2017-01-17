"""Initial version.

Revision ID: f13042810d4c
Revises:
Create Date: 2017-01-04 13:05:52.194339
"""
import sqlalchemy as sa
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

revision = 'f13042810d4c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.create_table(
        'assets_version',
        sa.Column('source_path', sa.String(length=1000), autoincrement=False, nullable=True),
        sa.Column('filename', sa.String(length=1000), autoincrement=False, nullable=True),
        sa.Column('content_type', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('size', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('width', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('height', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('raw_metadata', types.JSONType(), autoincrement=False, nullable=True),
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('title', sa.String(), autoincrement=False, nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('type', sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column('owner', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('professional_id', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('uploaded_by', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('assignment_id', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('history', types.JSONType(), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_assets_version_end_transaction_id'),
        'assets_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_assets_version_operation_type'),
        'assets_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_assets_version_slug'),
        'assets_version', ['slug'], unique=False)
    op.create_index(
        op.f('ix_assets_version_transaction_id'),
        'assets_version', ['transaction_id'], unique=False)

    op.create_table(
        'assignments_version',
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('payout_currency', types.CurrencyType(length=3), autoincrement=False,
                  nullable=True),
        sa.Column('payout_value', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('travel_expenses', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('additional_compensation', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('payable', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('scheduled_datetime', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('set_type', types.ChoiceType(choices=TypesOfSetChoices, impl=sa.String()),
                  autoincrement=False, nullable=True),
        sa.Column('order_id', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('pool_id', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('professional_id', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('submission_path', types.URLType(), autoincrement=False, nullable=True),
        sa.Column('total_assets', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('total_approvable_assets', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_assignments_version_end_transaction_id'),
        'assignments_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_assignments_version_operation_type'),
        'assignments_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_assignments_version_slug'),
        'assignments_version', ['slug'], unique=False)
    op.create_index(
        op.f('ix_assignments_version_transaction_id'),
        'assignments_version', ['transaction_id'], unique=False)

    op.create_table(
        'comments',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('comment_order', sa.Integer(), nullable=True),
        sa.Column('author_id', types.UUIDType(), nullable=False),
        sa.Column('in_reply_to', types.UUIDType(), nullable=True),
        sa.Column('entity_type', sa.String(length=255), nullable=True),
        sa.Column('entity_id', types.UUIDType(), nullable=True),
        sa.ForeignKeyConstraint(['in_reply_to'], ['comments.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )

    op.create_table(
        'customers',
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('tax_id_type', sa.String(length=50), nullable=True),
        sa.Column('tax_country', types.CountryType(length=2), nullable=True),
        sa.Column('parent_customer_id', types.UUIDType(), nullable=True),
        sa.Column('legal_name', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['parent_customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_customers_slug'), 'customers', ['slug'], unique=False)

    op.create_table(
        'customers_version',
        sa.Column('external_id', sa.String(), autoincrement=False, nullable=True),
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('title', sa.String(), autoincrement=False, nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('tax_id', sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column('tax_id_type', sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column('tax_country', types.CountryType(length=2), autoincrement=False,
                  nullable=True),
        sa.Column('parent_customer_id', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('legal_name', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_customers_version_end_transaction_id'),
        'customers_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_customers_version_operation_type'),
        'customers_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_customers_version_slug'),
        'customers_version', ['slug'], unique=False)
    op.create_index(
        op.f('ix_customers_version_transaction_id'),
        'customers_version', ['transaction_id'], unique=False)

    op.create_table(
        'images_version',
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_images_version_end_transaction_id'),
        'images_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_images_version_operation_type'),
        'images_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_images_version_transaction_id'),
        'images_version', ['transaction_id'], unique=False)

    op.create_table(
        'localroles',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('entity_type', sa.String(length=255), nullable=False),
        sa.Column('entity_id', types.UUIDType(), nullable=False),
        sa.Column('user_id', types.UUIDType(), nullable=False),
        sa.Column('role_name', types.ChoiceType(choices=LocalRolesChoices, impl=sa.String()),
                  nullable=False),
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

    op.create_table(
        'orderlocations_version',
        sa.Column('country', types.CountryType(length=2), autoincrement=False,
                  nullable=True),
        sa.Column('locality', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('formatted_address', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('info', types.JSONType(), autoincrement=False, nullable=True),
        sa.Column('timezone', types.TimezoneType(), autoincrement=False,
                  nullable=True),
        sa.Column('coordinates', geo.POINT(), autoincrement=False, nullable=True),
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('first_name', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('last_name', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('email', types.EmailType(length=255), autoincrement=False,
                  nullable=True),
        sa.Column('mobile', types.PhoneNumberType(length=20),
                  autoincrement=False, nullable=True),
        sa.Column('additional_phone', types.PhoneNumberType(length=20),
                  autoincrement=False, nullable=True),
        sa.Column('order_id', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_orderlocations_version_end_transaction_id'),
        'orderlocations_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_orderlocations_version_operation_type'),
        'orderlocations_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_orderlocations_version_transaction_id'),
        'orderlocations_version', ['transaction_id'], unique=False)

    op.create_table(
        'orders_version',
        sa.Column('external_id', sa.String(), autoincrement=False, nullable=True),
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('title', sa.String(), autoincrement=False, nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('price_currency', types.CurrencyType(length=3), autoincrement=False,
                  nullable=True),
        sa.Column('price', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('customer_order_id', sa.String(), autoincrement=False, nullable=True),
        sa.Column('job_id', sa.String(), autoincrement=False, nullable=True),
        sa.Column('customer_id', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('project_id', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('category', types.ChoiceType(choices=CategoryChoices, impl=sa.String()),
                  autoincrement=False, nullable=True),
        sa.Column('source', types.ChoiceType(choices=OrderInputSource, impl=sa.String()),
                  autoincrement=False, nullable=True),
        sa.Column('number_required_assets', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('requirements', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('availability', types.JSONType(), autoincrement=False, nullable=True),
        sa.Column('delivery', types.JSONType(), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_orders_version_customer_order_id'),
        'orders_version', ['customer_order_id'], unique=False)
    op.create_index(
        op.f('ix_orders_version_end_transaction_id'),
        'orders_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_orders_version_job_id'),
        'orders_version', ['job_id'], unique=False)
    op.create_index(
        op.f('ix_orders_version_operation_type'),
        'orders_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_orders_version_slug'),
        'orders_version', ['slug'], unique=False)
    op.create_index(
        op.f('ix_orders_version_transaction_id'),
        'orders_version', ['transaction_id'], unique=False)

    op.create_table(
        'photographers_version',
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_photographers_version_end_transaction_id'),
        'photographers_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_photographers_version_operation_type'),
        'photographers_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_photographers_version_transaction_id'),
        'photographers_version', ['transaction_id'], unique=False)

    op.create_table(
        'pools',
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('country', types.CountryType(length=2), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_pools_slug'), 'pools', ['slug'], unique=False)
    op.create_table(
        'pools_version',
        sa.Column('external_id', sa.String(), autoincrement=False, nullable=True),
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('title', sa.String(), autoincrement=False, nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('country', types.CountryType(length=2), autoincrement=False,
                  nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_pools_version_end_transaction_id'),
        'pools_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_pools_version_operation_type'),
        'pools_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_pools_version_slug'),
        'pools_version', ['slug'], unique=False)
    op.create_index(
        op.f('ix_pools_version_transaction_id'),
        'pools_version', ['transaction_id'], unique=False)

    op.create_table(
        'professionals',
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=False),
        sa.Column('last_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('gender', types.ChoiceType(choices=GenderCategories, impl=sa.String()),
                  nullable=True),
        sa.Column('accept_travel', sa.Boolean(), default=False),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('internal', sa.Boolean(), nullable=True),
        sa.Column('partners', sa.Boolean(), nullable=True),
        sa.Column('main_email', types.EmailType(length=255), nullable=True),
        sa.Column('main_mobile', types.PhoneNumberType(length=20), nullable=True),
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('photo_path', sa.String(length=255), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_professionals_slug'), 'professionals', ['slug'], unique=False)
    op.create_index(
        op.f('ix_professionals_accept_travel'),
        'professionals', ['accept_travel'], unique=False)

    op.create_table(
        'professionals_in_pool_version',
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('pool_id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('professional_id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('pool_id', 'professional_id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_professionals_in_pool_version_end_transaction_id'),
        'professionals_in_pool_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_professionals_in_pool_version_operation_type'),
        'professionals_in_pool_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_professionals_in_pool_version_transaction_id'),
        'professionals_in_pool_version', ['transaction_id'], unique=False)

    op.create_table(
        'professionals_version',
        sa.Column('external_id', sa.String(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('first_name', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('last_name', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('gender', types.ChoiceType(choices=GenderCategories, impl=sa.String()),
                  autoincrement=False, nullable=True),
        sa.Column('accept_travel', sa.Boolean(), default=False),
        sa.Column('birth_date', sa.Date(), autoincrement=False, nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('internal', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('partners', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('main_email', types.EmailType(length=255), autoincrement=False, nullable=True),
        sa.Column('main_mobile', types.PhoneNumberType(length=20), autoincrement=False,
                  nullable=True),
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('photo_path', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('type', sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_professionals_version_end_transaction_id'),
        'professionals_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_professionals_version_operation_type'),
        'professionals_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_professionals_version_slug'),
        'professionals_version', ['slug'], unique=False)
    op.create_index(
        op.f('ix_professionals_version_accept_travel'),
        'professionals_version', ['accept_travel'], unique=False)
    op.create_index(
        op.f('ix_professionals_version_transaction_id'),
        'professionals_version', ['transaction_id'], unique=False)

    op.create_table(
        'projects_version',
        sa.Column('external_id', sa.String(), autoincrement=False, nullable=True),
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('title', sa.String(), autoincrement=False, nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('abstract', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('number_required_assets', sa.Integer(), nullable=True),
        sa.Column('payout_currency', types.CurrencyType(length=3), autoincrement=False,
                  nullable=True),
        sa.Column('payout_value', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('price_currency', types.CurrencyType(length=3), autoincrement=False,
                  nullable=True),
        sa.Column('price', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('contract', types.URLType(), autoincrement=False, nullable=True),
        sa.Column('customer_id', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('tech_requirements', types.JSONType(), autoincrement=False, nullable=True),
        sa.Column('cancellation_window', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('availability_window', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('approval_window', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('total_orders', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('briefing', types.URLType(), autoincrement=False, nullable=True),
        sa.Column('release_template', types.URLType(), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_projects_version_end_transaction_id'),
        'projects_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_projects_version_operation_type'),
        'projects_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_projects_version_slug'),
        'projects_version', ['slug'], unique=False)
    op.create_index(
        op.f('ix_projects_version_transaction_id'),
        'projects_version', ['transaction_id'], unique=False)

    op.create_table(
        'threesixtyimages_version',
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_threesixtyimages_version_end_transaction_id'),
        'threesixtyimages_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_threesixtyimages_version_operation_type'),
        'threesixtyimages_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_threesixtyimages_version_transaction_id'),
        'threesixtyimages_version', ['transaction_id'], unique=False)

    op.create_table(
        'transaction',
        sa.Column('issued_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('remote_addr', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'videographers_version',
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_videographers_version_end_transaction_id'),
        'videographers_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_videographers_version_operation_type'),
        'videographers_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_videographers_version_transaction_id'),
        'videographers_version', ['transaction_id'], unique=False)

    op.create_table(
        'videos_version',
        sa.Column('duration', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('codecs', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('audio_channels', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_videos_version_end_transaction_id'),
        'videos_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_videos_version_operation_type'),
        'videos_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_videos_version_transaction_id'),
        'videos_version', ['transaction_id'], unique=False)

    op.create_table(
        'customerbillingaddresses',
        sa.Column('country', types.CountryType(length=2), nullable=False),
        sa.Column('locality', sa.String(length=255), nullable=False),
        sa.Column('formatted_address', sa.String(length=255), nullable=True),
        sa.Column('info', types.JSONType(), nullable=True),
        sa.Column('timezone', types.TimezoneType(), nullable=True),
        sa.Column('coordinates', geo.POINT(), nullable=True),
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('customer_id', types.UUIDType(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )

    op.create_table(
        'customercontacts',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=False),
        sa.Column('last_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('customer_id', types.UUIDType(), nullable=False),
        sa.Column('type', types.ChoiceType(choices=ContactTypes, impl=sa.String()),
                  nullable=False),
        sa.Column('position', sa.String(length=255), nullable=True),
        sa.Column('email', types.EmailType(length=255), nullable=True),
        sa.Column('mobile', types.PhoneNumberType(length=20), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(
        op.f('ix_customercontacts_slug'),
        'customercontacts', ['slug'], unique=False)

    op.create_table(
        'links',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('professional_id', types.UUIDType(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('url', types.URLType(), nullable=False),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )

    op.create_table(
        'photographers',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'professionals_in_pool',
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('pool_id', types.UUIDType(), nullable=False),
        sa.Column('professional_id', types.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['pool_id'], ['pools.id'], ),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('pool_id', 'professional_id')
    )

    op.create_table(
        'projects',
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('abstract', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('number_required_assets', sa.Integer(), nullable=False),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('payout_currency', types.CurrencyType(length=3), nullable=True),
        sa.Column('payout_value', sa.Integer(), nullable=False),
        sa.Column('price_currency', types.CurrencyType(length=3), nullable=True),
        sa.Column('price', sa.Integer(), nullable=True),
        sa.Column('contract', types.URLType(), nullable=True),
        sa.Column('customer_id', types.UUIDType(), nullable=False),
        sa.Column('tech_requirements', types.JSONType(), nullable=True),
        sa.Column('cancellation_window', sa.Integer(), nullable=True),
        sa.Column('availability_window', sa.Integer(), nullable=True),
        sa.Column('approval_window', sa.Integer(), nullable=True),
        sa.Column('total_orders', sa.Integer(), nullable=True),
        sa.Column('briefing', types.URLType(), nullable=True),
        sa.Column('release_template', types.URLType(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_projects_slug'), 'projects', ['slug'], unique=False)

    op.create_table(
        'videographers',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'workinglocations',
        sa.Column('country', types.CountryType(length=2), nullable=False),
        sa.Column('locality', sa.String(length=255), nullable=False),
        sa.Column('formatted_address', sa.String(length=255), nullable=True),
        sa.Column('info', types.JSONType(), nullable=True),
        sa.Column('timezone', types.TimezoneType(), nullable=True),
        sa.Column('coordinates', geo.POINT(), nullable=True),
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('professional_id', types.UUIDType(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('range', sa.Integer(), nullable=True),
        sa.Column('range_unit', types.ChoiceType(choices=DistanceUnits, impl=sa.String(5)),
                  nullable=True),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )

    op.create_table(
        'orders',
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('price_currency', types.CurrencyType(length=3), nullable=True),
        sa.Column('price', sa.Integer(), nullable=True),
        sa.Column('customer_order_id', sa.String(), nullable=True),
        sa.Column('job_id', sa.String(), nullable=True),
        sa.Column('customer_id', types.UUIDType(), nullable=True),
        sa.Column('project_id', types.UUIDType(), nullable=False),
        sa.Column('category', types.ChoiceType(choices=CategoryChoices, impl=sa.String()),
                  nullable=True),
        sa.Column('source', types.ChoiceType(choices=OrderInputSource, impl=sa.String()),
                  nullable=False),
        sa.Column('number_required_assets', sa.Integer(), nullable=False),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('availability', types.JSONType(), nullable=True),
        sa.Column('delivery', types.JSONType(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(
        op.f('ix_orders_customer_order_id'),
        'orders', ['customer_order_id'], unique=False)
    op.create_index(
        op.f('ix_orders_job_id'),
        'orders', ['job_id'], unique=False)
    op.create_index(
        op.f('ix_orders_slug'),
        'orders', ['slug'], unique=False)

    op.create_table(
        'assignments',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('payout_currency', types.CurrencyType(length=3), nullable=True),
        sa.Column('payout_value', sa.Integer(), nullable=False),
        sa.Column('travel_expenses', sa.Integer(), nullable=False),
        sa.Column('additional_compensation', sa.Integer(), nullable=False),
        sa.Column('payable', sa.Boolean(), nullable=False),
        sa.Column('scheduled_datetime', AwareDateTime(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('set_type', types.ChoiceType(choices=TypesOfSetChoices, impl=sa.String()),
                  nullable=True),
        sa.Column('order_id', types.UUIDType(), nullable=False),
        sa.Column('pool_id', types.UUIDType(), nullable=True),
        sa.Column('professional_id', types.UUIDType(), nullable=True),
        sa.Column('submission_path', types.URLType(), nullable=True),
        sa.Column('total_assets', sa.Integer(), nullable=True),
        sa.Column('total_approvable_assets', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['pool_id'], ['pools.id'], ),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(
        op.f('ix_assignments_slug'),
        'assignments', ['slug'], unique=False)

    op.create_table(
        'orderlocations',
        sa.Column('country', types.CountryType(length=2), nullable=False),
        sa.Column('locality', sa.String(length=255), nullable=False),
        sa.Column('formatted_address', sa.String(length=255), nullable=True),
        sa.Column('info', types.JSONType(), nullable=True),
        sa.Column('timezone', types.TimezoneType(), nullable=True),
        sa.Column('coordinates', geo.POINT(), nullable=True),
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('first_name', sa.String(length=255), nullable=False),
        sa.Column('last_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('email', types.EmailType(length=255), nullable=True),
        sa.Column('mobile', types.PhoneNumberType(length=20), nullable=True),
        sa.Column('additional_phone', types.PhoneNumberType(length=20), nullable=True),
        sa.Column('order_id', types.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )

    op.create_table(
        'assets',
        sa.Column('source_path', sa.String(length=1000), nullable=False),
        sa.Column('filename', sa.String(length=1000), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('size', sa.Integer(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('raw_metadata', types.JSONType(), nullable=True),
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('owner', sa.String(length=255), nullable=False),
        sa.Column('professional_id', types.UUIDType(), nullable=False),
        sa.Column('uploaded_by', types.UUIDType(), nullable=False),
        sa.Column('assignment_id', types.UUIDType(), nullable=False),
        sa.Column('history', types.JSONType(), nullable=True),
        sa.ForeignKeyConstraint(['assignment_id'], ['assignments.id'], ),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_assets_slug'), 'assets', ['slug'], unique=False)

    op.create_table(
        'images',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['assets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'threesixtyimages',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['assets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'videos',
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('codecs', sa.Text(), nullable=True),
        sa.Column('audio_channels', sa.Integer(), nullable=True),
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['assets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    """Downgrade database model."""
    op.drop_table('videos')
    op.drop_table('threesixtyimages')
    op.drop_table('images')
    op.drop_index(op.f('ix_assets_slug'), table_name='assets')
    op.drop_table('assets')
    op.drop_table('orderlocations')
    op.drop_index(op.f('ix_assignments_slug'), table_name='assignments')
    op.drop_table('assignments')
    op.drop_index(op.f('ix_orders_slug'), table_name='orders')
    op.drop_index(op.f('ix_orders_job_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_customer_order_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_table('workinglocations')
    op.drop_table('videographers')
    op.drop_index(op.f('ix_projects_slug'), table_name='projects')
    op.drop_table('projects')
    op.drop_table('professionals_in_pool')
    op.drop_table('photographers')
    op.drop_table('links')
    op.drop_index(op.f('ix_customercontacts_slug'), table_name='customercontacts')
    op.drop_table('customercontacts')
    op.drop_table('customerbillingaddresses')
    op.drop_index(op.f('ix_videos_version_transaction_id'), table_name='videos_version')
    op.drop_index(op.f('ix_videos_version_operation_type'), table_name='videos_version')
    op.drop_index(op.f('ix_videos_version_end_transaction_id'), table_name='videos_version')
    op.drop_table('videos_version')
    op.drop_index(
        op.f('ix_videographers_version_transaction_id'),
        table_name='videographers_version')
    op.drop_index(
        op.f('ix_videographers_version_operation_type'),
        table_name='videographers_version')
    op.drop_index(
        op.f('ix_videographers_version_end_transaction_id'),
        table_name='videographers_version')
    op.drop_table('videographers_version')
    op.drop_table('transaction')
    op.drop_index(
        op.f('ix_threesixtyimages_version_transaction_id'),
        table_name='threesixtyimages_version')
    op.drop_index(
        op.f('ix_threesixtyimages_version_operation_type'),
        table_name='threesixtyimages_version')
    op.drop_index(
        op.f('ix_threesixtyimages_version_end_transaction_id'),
        table_name='threesixtyimages_version')
    op.drop_table('threesixtyimages_version')
    op.drop_index(op.f('ix_projects_version_transaction_id'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_slug'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_operation_type'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_end_transaction_id'), table_name='projects_version')
    op.drop_table('projects_version')
    op.drop_index(
        op.f('ix_professionals_version_transaction_id'),
        table_name='professionals_version')
    op.drop_index(
        op.f('ix_professionals_version_slug'),
        table_name='professionals_version')
    op.drop_index(
        op.f('ix_professionals_version_operation_type'),
        table_name='professionals_version')
    op.drop_index(
        op.f('ix_professionals_version_end_transaction_id'),
        table_name='professionals_version')
    op.drop_table('professionals_version')
    op.drop_index(
        op.f('ix_professionals_in_pool_version_transaction_id'),
        table_name='professionals_in_pool_version')
    op.drop_index(
        op.f('ix_professionals_in_pool_version_operation_type'),
        table_name='professionals_in_pool_version')
    op.drop_index(
        op.f('ix_professionals_in_pool_version_end_transaction_id'),
        table_name='professionals_in_pool_version')
    op.drop_table('professionals_in_pool_version')
    op.drop_index(op.f('ix_professionals_slug'), table_name='professionals')
    op.drop_table('professionals')
    op.drop_index(op.f('ix_pools_version_transaction_id'), table_name='pools_version')
    op.drop_index(op.f('ix_pools_version_slug'), table_name='pools_version')
    op.drop_index(op.f('ix_pools_version_operation_type'), table_name='pools_version')
    op.drop_index(op.f('ix_pools_version_end_transaction_id'), table_name='pools_version')
    op.drop_table('pools_version')
    op.drop_index(op.f('ix_pools_slug'), table_name='pools')
    op.drop_table('pools')
    op.drop_index(
        op.f('ix_photographers_version_transaction_id'),
        table_name='photographers_version')
    op.drop_index(
        op.f('ix_photographers_version_operation_type'),
        table_name='photographers_version')
    op.drop_index(
        op.f('ix_photographers_version_end_transaction_id'),
        table_name='photographers_version')
    op.drop_table('photographers_version')
    op.drop_index(op.f('ix_orders_version_transaction_id'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_slug'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_operation_type'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_job_id'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_end_transaction_id'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_customer_order_id'), table_name='orders_version')
    op.drop_table('orders_version')
    op.drop_index(
        op.f('ix_orderlocations_version_transaction_id'),
        table_name='orderlocations_version')
    op.drop_index(
        op.f('ix_orderlocations_version_operation_type'),
        table_name='orderlocations_version')
    op.drop_index(
        op.f('ix_orderlocations_version_end_transaction_id'),
        table_name='orderlocations_version')
    op.drop_table('orderlocations_version')
    op.drop_index(op.f('ix_localroles_user_id'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_entity_type'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_entity_id'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_can_view'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_can_list'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_can_edit'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_can_delete'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_can_create'), table_name='localroles')
    op.drop_table('localroles')
    op.drop_index(op.f('ix_images_version_transaction_id'), table_name='images_version')
    op.drop_index(op.f('ix_images_version_operation_type'), table_name='images_version')
    op.drop_index(op.f('ix_images_version_end_transaction_id'), table_name='images_version')
    op.drop_table('images_version')
    op.drop_index(op.f('ix_customers_version_transaction_id'), table_name='customers_version')
    op.drop_index(op.f('ix_customers_version_slug'), table_name='customers_version')
    op.drop_index(op.f('ix_customers_version_operation_type'), table_name='customers_version')
    op.drop_index(op.f('ix_customers_version_end_transaction_id'), table_name='customers_version')
    op.drop_table('customers_version')
    op.drop_index(op.f('ix_customers_slug'), table_name='customers')
    op.drop_table('customers')
    op.drop_table('comments')
    op.drop_index(
        op.f('ix_assignments_version_transaction_id'),
        table_name='assignments_version')
    op.drop_index(op.f('ix_assignments_version_slug'), table_name='assignments_version')
    op.drop_index(op.f('ix_assignments_version_operation_type'), table_name='assignments_version')
    op.drop_index(
        op.f('ix_assignments_version_end_transaction_id'),
        table_name='assignments_version')
    op.drop_table('assignments_version')
    op.drop_index(op.f('ix_assets_version_transaction_id'), table_name='assets_version')
    op.drop_index(op.f('ix_assets_version_slug'), table_name='assets_version')
    op.drop_index(op.f('ix_assets_version_operation_type'), table_name='assets_version')
    op.drop_index(op.f('ix_assets_version_end_transaction_id'), table_name='assets_version')
    op.drop_table('assets_version')
