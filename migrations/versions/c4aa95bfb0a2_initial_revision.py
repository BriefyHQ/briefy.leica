"""initial revision.

Revision ID: c4aa95bfb0a2
Revises:
Create Date: 2017-01-21 18:15:29.041743
"""
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


import sqlalchemy as sa
import sqlalchemy_utils

revision = 'c4aa95bfb0a2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.create_table('assets_version',
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
    op.create_index(op.f('ix_assets_version_end_transaction_id'), 'assets_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_assets_version_operation_type'), 'assets_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_assets_version_slug'), 'assets_version', ['slug'], unique=False)
    op.create_index(op.f('ix_assets_version_transaction_id'), 'assets_version', ['transaction_id'], unique=False)
    op.create_table('assignments_version',
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
    sa.Column('payout_currency', types.CurrencyType(length=3), autoincrement=False, nullable=True),
    sa.Column('payout_value', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('travel_expenses', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('additional_compensation', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('reason_additional_compensation', sa.Text(), nullable=True, default=''),
    sa.Column('payable', sa.Boolean(), autoincrement=False, nullable=True),
    sa.Column('scheduled_datetime', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
    sa.Column('set_type', types.ChoiceType(
        choices=TypesOfSetChoices, impl=sa.String()
    ), autoincrement=False, nullable=True),
    sa.Column('order_id', types.UUIDType(), autoincrement=False, nullable=True),
    sa.Column('pool_id', types.UUIDType(), autoincrement=False, nullable=True),
    sa.Column('professional_id', types.UUIDType(), autoincrement=False, nullable=True),
    sa.Column('submission_path', types.URLType(), autoincrement=False, nullable=True),
    sa.Column('release_contract', types.URLType(), autoincrement=False, nullable=True),
    sa.Column('total_assets', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('total_approvable_assets', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_assignments_version_end_transaction_id'), 'assignments_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_assignments_version_operation_type'), 'assignments_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_assignments_version_slug'), 'assignments_version', ['slug'], unique=False)
    op.create_index(op.f('ix_assignments_version_transaction_id'), 'assignments_version', ['transaction_id'], unique=False)
    op.create_table('briefyuserprofiles_version',
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_briefyuserprofiles_version_end_transaction_id'), 'briefyuserprofiles_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_briefyuserprofiles_version_operation_type'), 'briefyuserprofiles_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_briefyuserprofiles_version_transaction_id'), 'briefyuserprofiles_version', ['transaction_id'], unique=False)
    op.create_table('comments',
    sa.Column('id', types.UUIDType(), nullable=False),
    sa.Column('created_at', AwareDateTime(), nullable=True),
    sa.Column('updated_at', AwareDateTime(), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('state_history', types.JSONType(), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('comment_order', sa.Integer(), nullable=True),
    sa.Column('author_id', types.UUIDType(), nullable=False),
    sa.Column('author_role', sa.String(), nullable=False),
    sa.Column('to_role', sa.String(), nullable=False),
    sa.Column('in_reply_to', types.UUIDType(), nullable=True),
    sa.Column('internal', sa.Boolean(), nullable=True),
    sa.Column('entity_type', sa.String(length=255), nullable=True),
    sa.Column('entity_id', types.UUIDType(), nullable=True),
    sa.ForeignKeyConstraint(['in_reply_to'], ['comments.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('customers',
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
    op.create_table('customers_version',
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
    sa.Column('tax_country', types.CountryType(length=2), autoincrement=False, nullable=True),
    sa.Column('parent_customer_id', types.UUIDType(), autoincrement=False, nullable=True),
    sa.Column('legal_name', sa.String(length=255), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_customers_version_end_transaction_id'), 'customers_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_customers_version_operation_type'), 'customers_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_customers_version_slug'), 'customers_version', ['slug'], unique=False)
    op.create_index(op.f('ix_customers_version_transaction_id'), 'customers_version', ['transaction_id'], unique=False)
    op.create_table('customeruserprofiles_version',
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_customeruserprofiles_version_end_transaction_id'), 'customeruserprofiles_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_customeruserprofiles_version_operation_type'), 'customeruserprofiles_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_customeruserprofiles_version_transaction_id'), 'customeruserprofiles_version', ['transaction_id'], unique=False)
    op.create_table('images_version',
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_images_version_end_transaction_id'), 'images_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_images_version_operation_type'), 'images_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_images_version_transaction_id'), 'images_version', ['transaction_id'], unique=False)
    op.create_table('localroles',
    sa.Column('id', types.UUIDType(), nullable=False),
    sa.Column('created_at', AwareDateTime(), nullable=True),
    sa.Column('updated_at', AwareDateTime(), nullable=True),
    sa.Column('entity_type', sa.String(length=255), nullable=False),
    sa.Column('entity_id', types.UUIDType(), nullable=False),
    sa.Column('user_id', types.UUIDType(), nullable=False),
    sa.Column('role_name', types.ChoiceType(
        choices=LocalRolesChoices, impl=sa.String()), nullable=False),
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
    op.create_table('orderlocations_version',
    sa.Column('country', types.CountryType(length=2), autoincrement=False, nullable=True),
    sa.Column('locality', sa.String(length=255), autoincrement=False, nullable=True),
    sa.Column('formatted_address', sa.String(length=255), autoincrement=False, nullable=True),
    sa.Column('info', types.JSONType(), autoincrement=False, nullable=True),
    sa.Column('timezone', types.TimezoneType(), autoincrement=False, nullable=True),
    sa.Column('coordinates', geo.POINT(), autoincrement=False, nullable=True),
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('first_name', sa.String(length=255), autoincrement=False, nullable=True),
    sa.Column('last_name', sa.String(length=255), autoincrement=False, nullable=True),
    sa.Column('company_name', sa.String(), autoincrement=False, nullable=True),
    sa.Column('email', types.EmailType(length=255), autoincrement=False, nullable=True),
    sa.Column('mobile', types.PhoneNumberType(length=20), autoincrement=False, nullable=True),
    sa.Column('additional_phone', types.PhoneNumberType(length=20), autoincrement=False, nullable=True),
    sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
    sa.Column('order_id', types.UUIDType(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_orderlocations_version_end_transaction_id'), 'orderlocations_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_orderlocations_version_operation_type'), 'orderlocations_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_orderlocations_version_transaction_id'), 'orderlocations_version', ['transaction_id'], unique=False)
    op.create_table('orders_version',
    sa.Column('external_id', sa.String(), autoincrement=False, nullable=True),
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('title', sa.String(), autoincrement=False, nullable=True),
    sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
    sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
    sa.Column('price_currency', types.CurrencyType(length=3), autoincrement=False, nullable=True),
    sa.Column('price', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('customer_order_id', sa.String(), autoincrement=False, nullable=True),
    sa.Column('job_id', sa.String(), autoincrement=False, nullable=True),
    sa.Column('customer_id', types.UUIDType(), autoincrement=False, nullable=True),
    sa.Column('project_id', types.UUIDType(), autoincrement=False, nullable=True),
    sa.Column('category', types.ChoiceType(choices=CategoryChoices, impl=sa.String()),
              autoincrement=False, nullable=True),
    sa.Column('source', types.ChoiceType(
        choices=OrderInputSource, impl=sa.String()
    ), autoincrement=False, nullable=True),
    sa.Column('number_required_assets', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('requirements', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('availability', types.JSONType(), autoincrement=False, nullable=True),
    sa.Column('delivery', types.JSONType(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_orders_version_customer_order_id'), 'orders_version', ['customer_order_id'], unique=False)
    op.create_index(op.f('ix_orders_version_end_transaction_id'), 'orders_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_orders_version_job_id'), 'orders_version', ['job_id'], unique=False)
    op.create_index(op.f('ix_orders_version_operation_type'), 'orders_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_orders_version_slug'), 'orders_version', ['slug'], unique=False)
    op.create_index(op.f('ix_orders_version_transaction_id'), 'orders_version', ['transaction_id'], unique=False)
    op.create_table('photographers_version',
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_photographers_version_end_transaction_id'), 'photographers_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_photographers_version_operation_type'), 'photographers_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_photographers_version_transaction_id'), 'photographers_version', ['transaction_id'], unique=False)
    op.create_table('pools',
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
    op.create_table('pools_version',
    sa.Column('external_id', sa.String(), autoincrement=False, nullable=True),
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('title', sa.String(), autoincrement=False, nullable=True),
    sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
    sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
    sa.Column('country', types.CountryType(length=2), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_pools_version_end_transaction_id'), 'pools_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_pools_version_operation_type'), 'pools_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_pools_version_slug'), 'pools_version', ['slug'], unique=False)
    op.create_index(op.f('ix_pools_version_transaction_id'), 'pools_version', ['transaction_id'], unique=False)
    op.create_table('professionals_in_pool_version',
    sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('pool_id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('professional_id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('pool_id', 'professional_id', 'transaction_id')
    )
    op.create_index(op.f('ix_professionals_in_pool_version_end_transaction_id'), 'professionals_in_pool_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_professionals_in_pool_version_operation_type'), 'professionals_in_pool_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_professionals_in_pool_version_transaction_id'), 'professionals_in_pool_version', ['transaction_id'], unique=False)
    op.create_table('professionals_version',
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('accept_travel', sa.Boolean(), autoincrement=False, nullable=True),
    sa.Column('photo_path', sa.String(length=255), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_professionals_version_accept_travel'), 'professionals_version', ['accept_travel'], unique=False)
    op.create_index(op.f('ix_professionals_version_end_transaction_id'), 'professionals_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_professionals_version_operation_type'), 'professionals_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_professionals_version_transaction_id'), 'professionals_version', ['transaction_id'], unique=False)
    op.create_table('projects_version',
    sa.Column('external_id', sa.String(), autoincrement=False, nullable=True),
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('title', sa.String(), autoincrement=False, nullable=True),
    sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
    sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
    sa.Column('payout_currency', types.CurrencyType(length=3), autoincrement=False, nullable=True),
    sa.Column('payout_value', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('price_currency', types.CurrencyType(length=3), autoincrement=False, nullable=True),
    sa.Column('category', types.ChoiceType(
        choices=CategoryChoices, impl=sa.String()), nullable=True),
    sa.Column('price', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('contract', types.URLType(), autoincrement=False, nullable=True),
    sa.Column('customer_id', types.UUIDType(), autoincrement=False, nullable=True),
    sa.Column('abstract', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('number_required_assets', sa.Integer(), autoincrement=False, nullable=True),
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
    op.create_index(op.f('ix_projects_version_end_transaction_id'), 'projects_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_projects_version_operation_type'), 'projects_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_projects_version_slug'), 'projects_version', ['slug'], unique=False)
    op.create_index(op.f('ix_projects_version_transaction_id'), 'projects_version', ['transaction_id'], unique=False)
    op.create_table('threesixtyimages_version',
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_threesixtyimages_version_end_transaction_id'), 'threesixtyimages_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_threesixtyimages_version_operation_type'), 'threesixtyimages_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_threesixtyimages_version_transaction_id'), 'threesixtyimages_version', ['transaction_id'], unique=False)
    op.create_table('transaction',
    sa.Column('issued_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('remote_addr', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('userprofiles',
    sa.Column('external_id', sa.String(), nullable=True),
    sa.Column('slug', sa.String(length=255), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=False),
    sa.Column('last_name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('gender', types.ChoiceType(choices=GenderCategories, impl=sa.String()), nullable=True),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('company_name', sa.String(), nullable=True),
    sa.Column('email', types.EmailType(length=255), nullable=True),
    sa.Column('mobile', types.PhoneNumberType(length=20), nullable=True),
    sa.Column('additional_phone', types.PhoneNumberType(length=20), nullable=True),
    sa.Column('internal', sa.Boolean(), nullable=True),
    sa.Column('partners', sa.Boolean(), nullable=True),
    sa.Column('created_at', AwareDateTime(), nullable=True),
    sa.Column('updated_at', AwareDateTime(), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('state_history', types.JSONType(), nullable=True),
    sa.Column('id', types.UUIDType(), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_userprofiles_slug'), 'userprofiles', ['slug'], unique=False)
    op.create_table('userprofiles_version',
    sa.Column('external_id', sa.String(), autoincrement=False, nullable=True),
    sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
    sa.Column('first_name', sa.String(length=255), autoincrement=False, nullable=True),
    sa.Column('last_name', sa.String(length=255), autoincrement=False, nullable=True),
    sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('gender', types.ChoiceType(choices=GenderCategories, impl=sa.String()), autoincrement=False, nullable=True),
    sa.Column('birth_date', sa.Date(), autoincrement=False, nullable=True),
    sa.Column('company_name', sa.String(), autoincrement=False, nullable=True),
    sa.Column('email', types.EmailType(length=255), autoincrement=False, nullable=True),
    sa.Column('mobile', types.PhoneNumberType(length=20), autoincrement=False, nullable=True),
    sa.Column('additional_phone', types.PhoneNumberType(length=20), autoincrement=False, nullable=True),
    sa.Column('internal', sa.Boolean(), autoincrement=False, nullable=True),
    sa.Column('partners', sa.Boolean(), autoincrement=False, nullable=True),
    sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
    sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('type', sa.String(length=50), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_userprofiles_version_end_transaction_id'), 'userprofiles_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_userprofiles_version_operation_type'), 'userprofiles_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_userprofiles_version_slug'), 'userprofiles_version', ['slug'], unique=False)
    op.create_index(op.f('ix_userprofiles_version_transaction_id'), 'userprofiles_version', ['transaction_id'], unique=False)
    op.create_table('videographers_version',
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_videographers_version_end_transaction_id'), 'videographers_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_videographers_version_operation_type'), 'videographers_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_videographers_version_transaction_id'), 'videographers_version', ['transaction_id'], unique=False)
    op.create_table('videos_version',
    sa.Column('duration', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('codecs', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('audio_channels', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_videos_version_end_transaction_id'), 'videos_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_videos_version_operation_type'), 'videos_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_videos_version_transaction_id'), 'videos_version', ['transaction_id'], unique=False)
    op.create_table('briefyuserprofiles',
    sa.Column('id', types.UUIDType(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['userprofiles.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('customerbillingaddresses',
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
    op.create_table('customercontacts',
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
    sa.Column('type', types.ChoiceType(
        choices=ContactTypes, impl=sa.String()
    ), nullable=False),
    sa.Column('position', sa.String(length=255), nullable=True),
    sa.Column('email', types.EmailType(length=255), nullable=True),
    sa.Column('mobile', types.PhoneNumberType(length=20), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_customercontacts_slug'), 'customercontacts', ['slug'], unique=False)
    op.create_table('customeruserprofiles',
    sa.Column('id', types.UUIDType(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['userprofiles.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('professionals',
    sa.Column('id', types.UUIDType(), nullable=False),
    sa.Column('accept_travel', sa.Boolean(), nullable=True),
    sa.Column('photo_path', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['userprofiles.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_professionals_accept_travel'), 'professionals', ['accept_travel'], unique=False)
    op.create_table('projects',
    sa.Column('external_id', sa.String(), nullable=True),
    sa.Column('id', types.UUIDType(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('slug', sa.String(length=255), nullable=True),
    sa.Column('created_at', AwareDateTime(), nullable=True),
    sa.Column('updated_at', AwareDateTime(), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('state_history', types.JSONType(), nullable=True),
    sa.Column('payout_currency', types.CurrencyType(length=3), nullable=True),
    sa.Column('payout_value', sa.Integer(), nullable=False),
    sa.Column('price_currency', types.CurrencyType(length=3), nullable=True),
    sa.Column('category', types.ChoiceType(
        choices=CategoryChoices, impl=sa.String()), nullable=False),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('contract', types.URLType(), nullable=True),
    sa.Column('customer_id', types.UUIDType(), nullable=False),
    sa.Column('abstract', sa.Text(), nullable=True),
    sa.Column('number_required_assets', sa.Integer(), nullable=True),
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
    op.create_table('links',
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
    op.create_table('orders',
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
    sa.Column('category', types.ChoiceType(
        choices=CategoryChoices, impl=sa.String()), nullable=True),
    sa.Column('source', types.ChoiceType(
        choices=OrderInputSource, impl=sa.String()
    ), nullable=False),
    sa.Column('number_required_assets', sa.Integer(), nullable=True),
    sa.Column('requirements', sa.Text(), nullable=True),
    sa.Column('availability', types.JSONType(), nullable=True),
    sa.Column('delivery', types.JSONType(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_orders_customer_order_id'), 'orders', ['customer_order_id'], unique=False)
    op.create_index(op.f('ix_orders_job_id'), 'orders', ['job_id'], unique=False)
    op.create_index(op.f('ix_orders_slug'), 'orders', ['slug'], unique=False)
    op.create_table('photographers',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_table('professionals_in_pool',
    sa.Column('created_at', AwareDateTime(), nullable=True),
    sa.Column('updated_at', AwareDateTime(), nullable=True),
    sa.Column('pool_id', types.UUIDType(), nullable=False),
    sa.Column('professional_id', types.UUIDType(), nullable=False),
    sa.ForeignKeyConstraint(['pool_id'], ['pools.id'], ),
    sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
    sa.PrimaryKeyConstraint('pool_id', 'professional_id')
    )
    op.create_table('videographers',
    sa.Column('id', types.UUIDType(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['professionals.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('workinglocations',
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
    sa.Column('range_unit', types.ChoiceType(
        choices=DistanceUnits, impl=sa.String(5)
    ), nullable=True),
    sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('assignments',
    sa.Column('id', types.UUIDType(), nullable=False),
    sa.Column('created_at', AwareDateTime(), nullable=True),
    sa.Column('updated_at', AwareDateTime(), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('state_history', types.JSONType(), nullable=True),
    sa.Column('payout_currency', types.CurrencyType(length=3), nullable=True),
    sa.Column('payout_value', sa.Integer(), nullable=False),
    sa.Column('travel_expenses', sa.Integer(), nullable=False),
    sa.Column('additional_compensation', sa.Integer(), nullable=False),
    sa.Column('reason_additional_compensation', sa.Text(), nullable=True, default=''),
    sa.Column('payable', sa.Boolean(), nullable=False),
    sa.Column('scheduled_datetime', AwareDateTime(), nullable=True),
    sa.Column('slug', sa.String(length=255), nullable=True),
    sa.Column('set_type', types.ChoiceType(
        choices=TypesOfSetChoices, impl=sa.String()
    ), nullable=True),
    sa.Column('order_id', types.UUIDType(), nullable=False),
    sa.Column('pool_id', types.UUIDType(), nullable=True),
    sa.Column('professional_id', types.UUIDType(), nullable=True),
    sa.Column('submission_path', types.URLType(), nullable=True),
    sa.Column('release_contract', types.URLType(), autoincrement=False, nullable=True),
    sa.Column('total_assets', sa.Integer(), nullable=True),
    sa.Column('total_approvable_assets', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['pool_id'], ['pools.id'], ),
    sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_assignments_slug'), 'assignments', ['slug'], unique=False)
    op.create_table('orderlocations',
    sa.Column('country', types.CountryType(length=2), nullable=False),
    sa.Column('locality', sa.String(length=255), nullable=False),
    sa.Column('formatted_address', sa.String(length=255), nullable=True),
    sa.Column('info', types.JSONType(), nullable=True),
    sa.Column('timezone', types.TimezoneType(), nullable=True),
    sa.Column('coordinates', geo.POINT(), nullable=True),
    sa.Column('id', types.UUIDType(), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=False),
    sa.Column('last_name', sa.String(length=255), nullable=False),
    sa.Column('company_name', sa.String(), nullable=True),
    sa.Column('email', types.EmailType(length=255), nullable=True),
    sa.Column('mobile', types.PhoneNumberType(length=20), nullable=True),
    sa.Column('additional_phone', types.PhoneNumberType(length=20), nullable=True),
    sa.Column('created_at', AwareDateTime(), nullable=True),
    sa.Column('updated_at', AwareDateTime(), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('state_history', types.JSONType(), nullable=True),
    sa.Column('order_id', types.UUIDType(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('assets',
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
    op.create_table('images',
    sa.Column('id', types.UUIDType(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['assets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('threesixtyimages',
    sa.Column('id', types.UUIDType(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['assets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('videos',
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('codecs', sa.Text(), nullable=True),
    sa.Column('audio_channels', sa.Integer(), nullable=True),
    sa.Column('id', types.UUIDType(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['assets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # create indexes
    op.create_index(op.f('ix_assets_assignment_id'), 'assets', ['assignment_id'], unique=False)
    op.create_index(op.f('ix_assets_created_at'), 'assets', ['created_at'], unique=False)
    op.create_index(op.f('ix_assets_professional_id'), 'assets', ['professional_id'], unique=False)
    op.create_index(op.f('ix_assets_title'), 'assets', ['title'], unique=False)
    op.create_index(op.f('ix_assets_updated_at'), 'assets', ['updated_at'], unique=False)
    op.create_unique_constraint(None, 'assets', ['id'])
    op.create_index(op.f('ix_assets_version_assignment_id'), 'assets_version', ['assignment_id'], unique=False)
    op.create_index(op.f('ix_assets_version_created_at'), 'assets_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_assets_version_professional_id'), 'assets_version', ['professional_id'], unique=False)
    op.create_index(op.f('ix_assets_version_title'), 'assets_version', ['title'], unique=False)
    op.create_index(op.f('ix_assets_version_updated_at'), 'assets_version', ['updated_at'], unique=False)
    op.create_index(op.f('ix_assignments_created_at'), 'assignments', ['created_at'], unique=False)
    op.create_index(op.f('ix_assignments_order_id'), 'assignments', ['order_id'], unique=False)
    op.create_index(op.f('ix_assignments_pool_id'), 'assignments', ['pool_id'], unique=False)
    op.create_index(op.f('ix_assignments_professional_id'), 'assignments', ['professional_id'], unique=False)
    op.create_index(op.f('ix_assignments_updated_at'), 'assignments', ['updated_at'], unique=False)
    op.create_unique_constraint(None, 'assignments', ['id'])
    op.create_index(op.f('ix_assignments_version_created_at'), 'assignments_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_assignments_version_order_id'), 'assignments_version', ['order_id'], unique=False)
    op.create_index(op.f('ix_assignments_version_pool_id'), 'assignments_version', ['pool_id'], unique=False)
    op.create_index(op.f('ix_assignments_version_professional_id'), 'assignments_version', ['professional_id'], unique=False)
    op.create_index(op.f('ix_assignments_version_updated_at'), 'assignments_version', ['updated_at'], unique=False)
    op.create_index(op.f('ix_briefyuserprofiles_id'), 'briefyuserprofiles', ['id'], unique=True)
    op.create_index(op.f('ix_briefyuserprofiles_version_id'), 'briefyuserprofiles_version', ['id'], unique=False)
    op.create_index(op.f('ix_comments_created_at'), 'comments', ['created_at'], unique=False)
    op.create_index(op.f('ix_comments_in_reply_to'), 'comments', ['in_reply_to'], unique=False)
    op.create_index(op.f('ix_comments_updated_at'), 'comments', ['updated_at'], unique=False)
    op.create_unique_constraint(None, 'comments', ['id'])
    op.create_index(op.f('ix_customerbillingaddresses_coordinates'), 'customerbillingaddresses', ['coordinates'], unique=False)
    op.create_index(op.f('ix_customerbillingaddresses_country'), 'customerbillingaddresses', ['country'], unique=False)
    op.create_index(op.f('ix_customerbillingaddresses_created_at'), 'customerbillingaddresses', ['created_at'], unique=False)
    op.create_index(op.f('ix_customerbillingaddresses_customer_id'), 'customerbillingaddresses', ['customer_id'], unique=False)
    op.create_index(op.f('ix_customerbillingaddresses_locality'), 'customerbillingaddresses', ['locality'], unique=False)
    op.create_index(op.f('ix_customerbillingaddresses_updated_at'), 'customerbillingaddresses', ['updated_at'], unique=False)
    op.drop_index('idx_customerbillingaddresses_coordinates', table_name='customerbillingaddresses')
    op.create_unique_constraint(None, 'customerbillingaddresses', ['id'])
    op.create_index(op.f('ix_customercontacts_created_at'), 'customercontacts', ['created_at'], unique=False)
    op.create_index(op.f('ix_customercontacts_customer_id'), 'customercontacts', ['customer_id'], unique=False)
    op.create_index(op.f('ix_customercontacts_first_name'), 'customercontacts', ['first_name'], unique=False)
    op.create_index(op.f('ix_customercontacts_last_name'), 'customercontacts', ['last_name'], unique=False)
    op.create_index(op.f('ix_customercontacts_title'), 'customercontacts', ['title'], unique=False)
    op.create_index(op.f('ix_customercontacts_updated_at'), 'customercontacts', ['updated_at'], unique=False)
    op.create_unique_constraint(None, 'customercontacts', ['id'])
    op.create_index(op.f('ix_customers_created_at'), 'customers', ['created_at'], unique=False)
    op.create_index(op.f('ix_customers_parent_customer_id'), 'customers', ['parent_customer_id'], unique=False)
    op.create_index(op.f('ix_customers_title'), 'customers', ['title'], unique=False)
    op.create_index(op.f('ix_customers_updated_at'), 'customers', ['updated_at'], unique=False)
    op.create_unique_constraint(None, 'customers', ['id'])
    op.create_index(op.f('ix_customers_version_created_at'), 'customers_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_customers_version_parent_customer_id'), 'customers_version', ['parent_customer_id'], unique=False)
    op.create_index(op.f('ix_customers_version_title'), 'customers_version', ['title'], unique=False)
    op.create_index(op.f('ix_customers_version_updated_at'), 'customers_version', ['updated_at'], unique=False)
    op.create_index(op.f('ix_customeruserprofiles_id'), 'customeruserprofiles', ['id'], unique=True)
    op.create_index(op.f('ix_customeruserprofiles_version_id'), 'customeruserprofiles_version', ['id'], unique=False)
    op.create_index(op.f('ix_images_id'), 'images', ['id'], unique=False)
    op.create_index(op.f('ix_images_version_id'), 'images_version', ['id'], unique=False)
    op.create_index(op.f('ix_links_created_at'), 'links', ['created_at'], unique=False)
    op.create_index(op.f('ix_links_professional_id'), 'links', ['professional_id'], unique=False)
    op.create_index(op.f('ix_links_updated_at'), 'links', ['updated_at'], unique=False)
    op.create_unique_constraint(None, 'links', ['id'])
    op.create_index(op.f('ix_localroles_created_at'), 'localroles', ['created_at'], unique=False)
    op.create_index(op.f('ix_localroles_role_name'), 'localroles', ['role_name'], unique=False)
    op.create_index(op.f('ix_localroles_updated_at'), 'localroles', ['updated_at'], unique=False)
    op.create_unique_constraint(None, 'localroles', ['id'])
    op.create_index(op.f('ix_orderlocations_coordinates'), 'orderlocations', ['coordinates'], unique=False)
    op.create_index(op.f('ix_orderlocations_country'), 'orderlocations', ['country'], unique=False)
    op.create_index(op.f('ix_orderlocations_created_at'), 'orderlocations', ['created_at'], unique=False)
    op.create_index(op.f('ix_orderlocations_first_name'), 'orderlocations', ['first_name'], unique=False)
    op.create_index(op.f('ix_orderlocations_last_name'), 'orderlocations', ['last_name'], unique=False)
    op.create_index(op.f('ix_orderlocations_locality'), 'orderlocations', ['locality'], unique=False)
    op.create_index(op.f('ix_orderlocations_order_id'), 'orderlocations', ['order_id'], unique=False)
    op.create_index(op.f('ix_orderlocations_updated_at'), 'orderlocations', ['updated_at'], unique=False)
    op.drop_index('idx_orderlocations_coordinates', table_name='orderlocations')
    op.create_unique_constraint(None, 'orderlocations', ['id'])
    op.create_index(op.f('ix_orderlocations_version_coordinates'), 'orderlocations_version', ['coordinates'], unique=False)
    op.create_index(op.f('ix_orderlocations_version_country'), 'orderlocations_version', ['country'], unique=False)
    op.create_index(op.f('ix_orderlocations_version_created_at'), 'orderlocations_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_orderlocations_version_first_name'), 'orderlocations_version', ['first_name'], unique=False)
    op.create_index(op.f('ix_orderlocations_version_last_name'), 'orderlocations_version', ['last_name'], unique=False)
    op.create_index(op.f('ix_orderlocations_version_locality'), 'orderlocations_version', ['locality'], unique=False)
    op.create_index(op.f('ix_orderlocations_version_order_id'), 'orderlocations_version', ['order_id'], unique=False)
    op.create_index(op.f('ix_orderlocations_version_updated_at'), 'orderlocations_version', ['updated_at'], unique=False)
    op.drop_index('idx_orderlocations_version_coordinates', table_name='orderlocations_version')
    op.drop_column('orderlocations_version', 'timezone')
    op.create_index(op.f('ix_orders_created_at'), 'orders', ['created_at'], unique=False)
    op.create_index(op.f('ix_orders_customer_id'), 'orders', ['customer_id'], unique=False)
    op.create_index(op.f('ix_orders_project_id'), 'orders', ['project_id'], unique=False)
    op.create_index(op.f('ix_orders_title'), 'orders', ['title'], unique=False)
    op.create_index(op.f('ix_orders_updated_at'), 'orders', ['updated_at'], unique=False)
    op.create_unique_constraint(None, 'orders', ['id'])
    op.create_index(op.f('ix_orders_version_created_at'), 'orders_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_orders_version_customer_id'), 'orders_version', ['customer_id'], unique=False)
    op.create_index(op.f('ix_orders_version_project_id'), 'orders_version', ['project_id'], unique=False)
    op.create_index(op.f('ix_orders_version_title'), 'orders_version', ['title'], unique=False)
    op.create_index(op.f('ix_orders_version_updated_at'), 'orders_version', ['updated_at'], unique=False)
    op.create_index(op.f('ix_photographers_id'), 'photographers', ['id'], unique=True)
    op.create_index(op.f('ix_photographers_version_id'), 'photographers_version', ['id'], unique=False)
    op.create_index(op.f('ix_pools_created_at'), 'pools', ['created_at'], unique=False)
    op.create_index(op.f('ix_pools_title'), 'pools', ['title'], unique=False)
    op.create_index(op.f('ix_pools_updated_at'), 'pools', ['updated_at'], unique=False)
    op.create_unique_constraint(None, 'pools', ['id'])
    op.create_index(op.f('ix_pools_version_created_at'), 'pools_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_pools_version_title'), 'pools_version', ['title'], unique=False)
    op.create_index(op.f('ix_pools_version_updated_at'), 'pools_version', ['updated_at'], unique=False)
    op.create_index(op.f('ix_professionals_id'), 'professionals', ['id'], unique=True)
    op.create_index(op.f('ix_professionals_in_pool_created_at'), 'professionals_in_pool', ['created_at'], unique=False)
    op.create_index(op.f('ix_professionals_in_pool_pool_id'), 'professionals_in_pool', ['pool_id'], unique=False)
    op.create_index(op.f('ix_professionals_in_pool_updated_at'), 'professionals_in_pool', ['updated_at'], unique=False)
    op.create_index(op.f('ix_professionals_in_pool_version_created_at'), 'professionals_in_pool_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_professionals_in_pool_version_pool_id'), 'professionals_in_pool_version', ['pool_id'], unique=False)
    op.create_index(op.f('ix_professionals_in_pool_version_updated_at'), 'professionals_in_pool_version', ['updated_at'], unique=False)
    op.create_index(op.f('ix_professionals_version_id'), 'professionals_version', ['id'], unique=False)
    op.create_index(op.f('ix_projects_created_at'), 'projects', ['created_at'], unique=False)
    op.create_index(op.f('ix_projects_customer_id'), 'projects', ['customer_id'], unique=False)
    op.create_index(op.f('ix_projects_title'), 'projects', ['title'], unique=False)
    op.create_index(op.f('ix_projects_updated_at'), 'projects', ['updated_at'], unique=False)
    op.create_unique_constraint(None, 'projects', ['id'])
    op.create_index(op.f('ix_projects_version_created_at'), 'projects_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_projects_version_customer_id'), 'projects_version', ['customer_id'], unique=False)
    op.create_index(op.f('ix_projects_version_title'), 'projects_version', ['title'], unique=False)
    op.create_index(op.f('ix_projects_version_updated_at'), 'projects_version', ['updated_at'], unique=False)
    op.create_index(op.f('ix_threesixtyimages_id'), 'threesixtyimages', ['id'], unique=False)
    op.create_index(op.f('ix_threesixtyimages_version_id'), 'threesixtyimages_version', ['id'], unique=False)
    op.create_index(op.f('ix_userprofiles_created_at'), 'userprofiles', ['created_at'], unique=False)
    op.create_index(op.f('ix_userprofiles_first_name'), 'userprofiles', ['first_name'], unique=False)
    op.create_index(op.f('ix_userprofiles_last_name'), 'userprofiles', ['last_name'], unique=False)
    op.create_index(op.f('ix_userprofiles_updated_at'), 'userprofiles', ['updated_at'], unique=False)
    op.create_unique_constraint(None, 'userprofiles', ['id'])
    op.create_index(op.f('ix_userprofiles_version_created_at'), 'userprofiles_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_userprofiles_version_first_name'), 'userprofiles_version', ['first_name'], unique=False)
    op.create_index(op.f('ix_userprofiles_version_last_name'), 'userprofiles_version', ['last_name'], unique=False)
    op.create_index(op.f('ix_userprofiles_version_updated_at'), 'userprofiles_version', ['updated_at'], unique=False)
    op.create_index(op.f('ix_videographers_id'), 'videographers', ['id'], unique=True)
    op.create_index(op.f('ix_videographers_version_id'), 'videographers_version', ['id'], unique=False)
    op.create_index(op.f('ix_videos_id'), 'videos', ['id'], unique=False)
    op.create_index(op.f('ix_videos_version_id'), 'videos_version', ['id'], unique=False)
    op.create_index(op.f('ix_workinglocations_coordinates'), 'workinglocations', ['coordinates'], unique=False)
    op.create_index(op.f('ix_workinglocations_country'), 'workinglocations', ['country'], unique=False)
    op.create_index(op.f('ix_workinglocations_created_at'), 'workinglocations', ['created_at'], unique=False)
    op.create_index(op.f('ix_workinglocations_locality'), 'workinglocations', ['locality'], unique=False)
    op.create_index(op.f('ix_workinglocations_professional_id'), 'workinglocations', ['professional_id'], unique=False)
    op.create_index(op.f('ix_workinglocations_updated_at'), 'workinglocations', ['updated_at'], unique=False)
    op.drop_index('idx_workinglocations_coordinates', table_name='workinglocations')
    op.create_unique_constraint(None, 'workinglocations', ['id'])


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
    op.drop_table('workinglocations')
    op.drop_table('videographers')
    op.drop_table('professionals_in_pool')
    op.drop_table('photographers')
    op.drop_index(op.f('ix_orders_slug'), table_name='orders')
    op.drop_index(op.f('ix_orders_job_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_customer_order_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_table('links')
    op.drop_index(op.f('ix_projects_slug'), table_name='projects')
    op.drop_table('projects')
    op.drop_index(op.f('ix_professionals_accept_travel'), table_name='professionals')
    op.drop_table('professionals')
    op.drop_table('customeruserprofiles')
    op.drop_index(op.f('ix_customercontacts_slug'), table_name='customercontacts')
    op.drop_table('customercontacts')
    op.drop_table('customerbillingaddresses')
    op.drop_table('briefyuserprofiles')
    op.drop_index(op.f('ix_videos_version_transaction_id'), table_name='videos_version')
    op.drop_index(op.f('ix_videos_version_operation_type'), table_name='videos_version')
    op.drop_index(op.f('ix_videos_version_end_transaction_id'), table_name='videos_version')
    op.drop_table('videos_version')
    op.drop_index(op.f('ix_videographers_version_transaction_id'), table_name='videographers_version')
    op.drop_index(op.f('ix_videographers_version_operation_type'), table_name='videographers_version')
    op.drop_index(op.f('ix_videographers_version_end_transaction_id'), table_name='videographers_version')
    op.drop_table('videographers_version')
    op.drop_index(op.f('ix_userprofiles_version_transaction_id'), table_name='userprofiles_version')
    op.drop_index(op.f('ix_userprofiles_version_slug'), table_name='userprofiles_version')
    op.drop_index(op.f('ix_userprofiles_version_operation_type'), table_name='userprofiles_version')
    op.drop_index(op.f('ix_userprofiles_version_end_transaction_id'), table_name='userprofiles_version')
    op.drop_table('userprofiles_version')
    op.drop_index(op.f('ix_userprofiles_slug'), table_name='userprofiles')
    op.drop_table('userprofiles')
    op.drop_table('transaction')
    op.drop_index(op.f('ix_threesixtyimages_version_transaction_id'), table_name='threesixtyimages_version')
    op.drop_index(op.f('ix_threesixtyimages_version_operation_type'), table_name='threesixtyimages_version')
    op.drop_index(op.f('ix_threesixtyimages_version_end_transaction_id'), table_name='threesixtyimages_version')
    op.drop_table('threesixtyimages_version')
    op.drop_index(op.f('ix_projects_version_transaction_id'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_slug'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_operation_type'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_end_transaction_id'), table_name='projects_version')
    op.drop_table('projects_version')
    op.drop_index(op.f('ix_professionals_version_transaction_id'), table_name='professionals_version')
    op.drop_index(op.f('ix_professionals_version_operation_type'), table_name='professionals_version')
    op.drop_index(op.f('ix_professionals_version_end_transaction_id'), table_name='professionals_version')
    op.drop_index(op.f('ix_professionals_version_accept_travel'), table_name='professionals_version')
    op.drop_table('professionals_version')
    op.drop_index(op.f('ix_professionals_in_pool_version_transaction_id'), table_name='professionals_in_pool_version')
    op.drop_index(op.f('ix_professionals_in_pool_version_operation_type'), table_name='professionals_in_pool_version')
    op.drop_index(op.f('ix_professionals_in_pool_version_end_transaction_id'), table_name='professionals_in_pool_version')
    op.drop_table('professionals_in_pool_version')
    op.drop_index(op.f('ix_pools_version_transaction_id'), table_name='pools_version')
    op.drop_index(op.f('ix_pools_version_slug'), table_name='pools_version')
    op.drop_index(op.f('ix_pools_version_operation_type'), table_name='pools_version')
    op.drop_index(op.f('ix_pools_version_end_transaction_id'), table_name='pools_version')
    op.drop_table('pools_version')
    op.drop_index(op.f('ix_pools_slug'), table_name='pools')
    op.drop_table('pools')
    op.drop_index(op.f('ix_photographers_version_transaction_id'), table_name='photographers_version')
    op.drop_index(op.f('ix_photographers_version_operation_type'), table_name='photographers_version')
    op.drop_index(op.f('ix_photographers_version_end_transaction_id'), table_name='photographers_version')
    op.drop_table('photographers_version')
    op.drop_index(op.f('ix_orders_version_transaction_id'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_slug'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_operation_type'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_job_id'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_end_transaction_id'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_customer_order_id'), table_name='orders_version')
    op.drop_table('orders_version')
    op.drop_index(op.f('ix_orderlocations_version_transaction_id'), table_name='orderlocations_version')
    op.drop_index(op.f('ix_orderlocations_version_operation_type'), table_name='orderlocations_version')
    op.drop_index(op.f('ix_orderlocations_version_end_transaction_id'), table_name='orderlocations_version')
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
    op.drop_index(op.f('ix_customeruserprofiles_version_transaction_id'), table_name='customeruserprofiles_version')
    op.drop_index(op.f('ix_customeruserprofiles_version_operation_type'), table_name='customeruserprofiles_version')
    op.drop_index(op.f('ix_customeruserprofiles_version_end_transaction_id'), table_name='customeruserprofiles_version')
    op.drop_table('customeruserprofiles_version')
    op.drop_index(op.f('ix_customers_version_transaction_id'), table_name='customers_version')
    op.drop_index(op.f('ix_customers_version_slug'), table_name='customers_version')
    op.drop_index(op.f('ix_customers_version_operation_type'), table_name='customers_version')
    op.drop_index(op.f('ix_customers_version_end_transaction_id'), table_name='customers_version')
    op.drop_table('customers_version')
    op.drop_index(op.f('ix_customers_slug'), table_name='customers')
    op.drop_table('customers')
    op.drop_table('comments')
    op.drop_index(op.f('ix_briefyuserprofiles_version_transaction_id'), table_name='briefyuserprofiles_version')
    op.drop_index(op.f('ix_briefyuserprofiles_version_operation_type'), table_name='briefyuserprofiles_version')
    op.drop_index(op.f('ix_briefyuserprofiles_version_end_transaction_id'), table_name='briefyuserprofiles_version')
    op.drop_table('briefyuserprofiles_version')
    op.drop_index(op.f('ix_assignments_version_transaction_id'), table_name='assignments_version')
    op.drop_index(op.f('ix_assignments_version_slug'), table_name='assignments_version')
    op.drop_index(op.f('ix_assignments_version_operation_type'), table_name='assignments_version')
    op.drop_index(op.f('ix_assignments_version_end_transaction_id'), table_name='assignments_version')
    op.drop_table('assignments_version')
    op.drop_index(op.f('ix_assets_version_transaction_id'), table_name='assets_version')
    op.drop_index(op.f('ix_assets_version_slug'), table_name='assets_version')
    op.drop_index(op.f('ix_assets_version_operation_type'), table_name='assets_version')
    op.drop_index(op.f('ix_assets_version_end_transaction_id'), table_name='assets_version')
    op.drop_table('assets_version')

    op.drop_constraint(None, 'workinglocations', type_='unique')
    op.create_index('idx_workinglocations_coordinates', 'workinglocations', ['coordinates'], unique=False)
    op.drop_index(op.f('ix_workinglocations_updated_at'), table_name='workinglocations')
    op.drop_index(op.f('ix_workinglocations_professional_id'), table_name='workinglocations')
    op.drop_index(op.f('ix_workinglocations_locality'), table_name='workinglocations')
    op.drop_index(op.f('ix_workinglocations_created_at'), table_name='workinglocations')
    op.drop_index(op.f('ix_workinglocations_country'), table_name='workinglocations')
    op.drop_index(op.f('ix_workinglocations_coordinates'), table_name='workinglocations')
    op.drop_index(op.f('ix_videos_version_id'), table_name='videos_version')
    op.drop_index(op.f('ix_videos_id'), table_name='videos')
    op.drop_index(op.f('ix_videographers_version_id'), table_name='videographers_version')
    op.drop_index(op.f('ix_videographers_id'), table_name='videographers')
    op.drop_index(op.f('ix_userprofiles_version_updated_at'), table_name='userprofiles_version')
    op.drop_index(op.f('ix_userprofiles_version_last_name'), table_name='userprofiles_version')
    op.drop_index(op.f('ix_userprofiles_version_first_name'), table_name='userprofiles_version')
    op.drop_index(op.f('ix_userprofiles_version_created_at'), table_name='userprofiles_version')
    op.drop_constraint(None, 'userprofiles', type_='unique')
    op.drop_index(op.f('ix_userprofiles_updated_at'), table_name='userprofiles')
    op.drop_index(op.f('ix_userprofiles_last_name'), table_name='userprofiles')
    op.drop_index(op.f('ix_userprofiles_first_name'), table_name='userprofiles')
    op.drop_index(op.f('ix_userprofiles_created_at'), table_name='userprofiles')
    op.drop_index(op.f('ix_threesixtyimages_version_id'), table_name='threesixtyimages_version')
    op.drop_index(op.f('ix_threesixtyimages_id'), table_name='threesixtyimages')
    op.drop_index(op.f('ix_projects_version_updated_at'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_title'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_customer_id'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_created_at'), table_name='projects_version')
    op.drop_constraint(None, 'projects', type_='unique')
    op.drop_index(op.f('ix_projects_updated_at'), table_name='projects')
    op.drop_index(op.f('ix_projects_title'), table_name='projects')
    op.drop_index(op.f('ix_projects_customer_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_created_at'), table_name='projects')
    op.drop_index(op.f('ix_professionals_version_id'), table_name='professionals_version')
    op.drop_index(op.f('ix_professionals_in_pool_version_updated_at'), table_name='professionals_in_pool_version')
    op.drop_index(op.f('ix_professionals_in_pool_version_pool_id'), table_name='professionals_in_pool_version')
    op.drop_index(op.f('ix_professionals_in_pool_version_created_at'), table_name='professionals_in_pool_version')
    op.drop_index(op.f('ix_professionals_in_pool_updated_at'), table_name='professionals_in_pool')
    op.drop_index(op.f('ix_professionals_in_pool_pool_id'), table_name='professionals_in_pool')
    op.drop_index(op.f('ix_professionals_in_pool_created_at'), table_name='professionals_in_pool')
    op.drop_index(op.f('ix_professionals_id'), table_name='professionals')
    op.drop_index(op.f('ix_pools_version_updated_at'), table_name='pools_version')
    op.drop_index(op.f('ix_pools_version_title'), table_name='pools_version')
    op.drop_index(op.f('ix_pools_version_created_at'), table_name='pools_version')
    op.drop_constraint(None, 'pools', type_='unique')
    op.drop_index(op.f('ix_pools_updated_at'), table_name='pools')
    op.drop_index(op.f('ix_pools_title'), table_name='pools')
    op.drop_index(op.f('ix_pools_created_at'), table_name='pools')
    op.drop_index(op.f('ix_photographers_version_id'), table_name='photographers_version')
    op.drop_index(op.f('ix_photographers_id'), table_name='photographers')
    op.drop_index(op.f('ix_orders_version_updated_at'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_title'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_project_id'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_customer_id'), table_name='orders_version')
    op.drop_index(op.f('ix_orders_version_created_at'), table_name='orders_version')
    op.drop_constraint(None, 'orders', type_='unique')
    op.drop_index(op.f('ix_orders_updated_at'), table_name='orders')
    op.drop_index(op.f('ix_orders_title'), table_name='orders')
    op.drop_index(op.f('ix_orders_project_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_customer_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_created_at'), table_name='orders')
    op.add_column('orderlocations_version', sa.Column('timezone', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.create_index('idx_orderlocations_version_coordinates', 'orderlocations_version', ['coordinates'], unique=False)
    op.drop_index(op.f('ix_orderlocations_version_updated_at'), table_name='orderlocations_version')
    op.drop_index(op.f('ix_orderlocations_version_order_id'), table_name='orderlocations_version')
    op.drop_index(op.f('ix_orderlocations_version_locality'), table_name='orderlocations_version')
    op.drop_index(op.f('ix_orderlocations_version_last_name'), table_name='orderlocations_version')
    op.drop_index(op.f('ix_orderlocations_version_first_name'), table_name='orderlocations_version')
    op.drop_index(op.f('ix_orderlocations_version_created_at'), table_name='orderlocations_version')
    op.drop_index(op.f('ix_orderlocations_version_country'), table_name='orderlocations_version')
    op.drop_index(op.f('ix_orderlocations_version_coordinates'), table_name='orderlocations_version')
    op.drop_constraint(None, 'orderlocations', type_='unique')
    op.create_index('idx_orderlocations_coordinates', 'orderlocations', ['coordinates'], unique=False)
    op.drop_index(op.f('ix_orderlocations_updated_at'), table_name='orderlocations')
    op.drop_index(op.f('ix_orderlocations_order_id'), table_name='orderlocations')
    op.drop_index(op.f('ix_orderlocations_locality'), table_name='orderlocations')
    op.drop_index(op.f('ix_orderlocations_last_name'), table_name='orderlocations')
    op.drop_index(op.f('ix_orderlocations_first_name'), table_name='orderlocations')
    op.drop_index(op.f('ix_orderlocations_created_at'), table_name='orderlocations')
    op.drop_index(op.f('ix_orderlocations_country'), table_name='orderlocations')
    op.drop_index(op.f('ix_orderlocations_coordinates'), table_name='orderlocations')
    op.drop_constraint(None, 'localroles', type_='unique')
    op.drop_index(op.f('ix_localroles_updated_at'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_role_name'), table_name='localroles')
    op.drop_index(op.f('ix_localroles_created_at'), table_name='localroles')
    op.drop_constraint(None, 'links', type_='unique')
    op.drop_index(op.f('ix_links_updated_at'), table_name='links')
    op.drop_index(op.f('ix_links_professional_id'), table_name='links')
    op.drop_index(op.f('ix_links_created_at'), table_name='links')
    op.drop_index(op.f('ix_images_version_id'), table_name='images_version')
    op.drop_index(op.f('ix_images_id'), table_name='images')
    op.drop_index(op.f('ix_customeruserprofiles_version_id'), table_name='customeruserprofiles_version')
    op.drop_index(op.f('ix_customeruserprofiles_id'), table_name='customeruserprofiles')
    op.drop_index(op.f('ix_customers_version_updated_at'), table_name='customers_version')
    op.drop_index(op.f('ix_customers_version_title'), table_name='customers_version')
    op.drop_index(op.f('ix_customers_version_parent_customer_id'), table_name='customers_version')
    op.drop_index(op.f('ix_customers_version_created_at'), table_name='customers_version')
    op.drop_constraint(None, 'customers', type_='unique')
    op.drop_index(op.f('ix_customers_updated_at'), table_name='customers')
    op.drop_index(op.f('ix_customers_title'), table_name='customers')
    op.drop_index(op.f('ix_customers_parent_customer_id'), table_name='customers')
    op.drop_index(op.f('ix_customers_created_at'), table_name='customers')
    op.drop_constraint(None, 'customercontacts', type_='unique')
    op.drop_index(op.f('ix_customercontacts_updated_at'), table_name='customercontacts')
    op.drop_index(op.f('ix_customercontacts_title'), table_name='customercontacts')
    op.drop_index(op.f('ix_customercontacts_last_name'), table_name='customercontacts')
    op.drop_index(op.f('ix_customercontacts_first_name'), table_name='customercontacts')
    op.drop_index(op.f('ix_customercontacts_customer_id'), table_name='customercontacts')
    op.drop_index(op.f('ix_customercontacts_created_at'), table_name='customercontacts')
    op.drop_constraint(None, 'customerbillingaddresses', type_='unique')
    op.create_index('idx_customerbillingaddresses_coordinates', 'customerbillingaddresses', ['coordinates'], unique=False)
    op.drop_index(op.f('ix_customerbillingaddresses_updated_at'), table_name='customerbillingaddresses')
    op.drop_index(op.f('ix_customerbillingaddresses_locality'), table_name='customerbillingaddresses')
    op.drop_index(op.f('ix_customerbillingaddresses_customer_id'), table_name='customerbillingaddresses')
    op.drop_index(op.f('ix_customerbillingaddresses_created_at'), table_name='customerbillingaddresses')
    op.drop_index(op.f('ix_customerbillingaddresses_country'), table_name='customerbillingaddresses')
    op.drop_index(op.f('ix_customerbillingaddresses_coordinates'), table_name='customerbillingaddresses')
    op.drop_constraint(None, 'comments', type_='unique')
    op.drop_index(op.f('ix_comments_updated_at'), table_name='comments')
    op.drop_index(op.f('ix_comments_in_reply_to'), table_name='comments')
    op.drop_index(op.f('ix_comments_created_at'), table_name='comments')
    op.drop_index(op.f('ix_briefyuserprofiles_version_id'), table_name='briefyuserprofiles_version')
    op.drop_index(op.f('ix_briefyuserprofiles_id'), table_name='briefyuserprofiles')
    op.drop_index(op.f('ix_assignments_version_updated_at'), table_name='assignments_version')
    op.drop_index(op.f('ix_assignments_version_professional_id'), table_name='assignments_version')
    op.drop_index(op.f('ix_assignments_version_pool_id'), table_name='assignments_version')
    op.drop_index(op.f('ix_assignments_version_order_id'), table_name='assignments_version')
    op.drop_index(op.f('ix_assignments_version_created_at'), table_name='assignments_version')
    op.drop_constraint(None, 'assignments', type_='unique')
    op.drop_index(op.f('ix_assignments_updated_at'), table_name='assignments')
    op.drop_index(op.f('ix_assignments_professional_id'), table_name='assignments')
    op.drop_index(op.f('ix_assignments_pool_id'), table_name='assignments')
    op.drop_index(op.f('ix_assignments_order_id'), table_name='assignments')
    op.drop_index(op.f('ix_assignments_created_at'), table_name='assignments')
    op.drop_index(op.f('ix_assets_version_updated_at'), table_name='assets_version')
    op.drop_index(op.f('ix_assets_version_title'), table_name='assets_version')
    op.drop_index(op.f('ix_assets_version_professional_id'), table_name='assets_version')
    op.drop_index(op.f('ix_assets_version_created_at'), table_name='assets_version')
    op.drop_index(op.f('ix_assets_version_assignment_id'), table_name='assets_version')
    op.drop_constraint(None, 'assets', type_='unique')
    op.drop_index(op.f('ix_assets_updated_at'), table_name='assets')
    op.drop_index(op.f('ix_assets_title'), table_name='assets')
    op.drop_index(op.f('ix_assets_professional_id'), table_name='assets')
    op.drop_index(op.f('ix_assets_created_at'), table_name='assets')
    op.drop_index(op.f('ix_assets_assignment_id'), table_name='assets')
