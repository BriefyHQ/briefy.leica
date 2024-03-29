"""Change permission model.

Revision ID: 90177ad0654d
Revises: cab6693525e6
Create Date: 2017-07-05 11:40:10.204660
"""
import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from briefy.common.db.types.aware_datetime import AwareDateTime
from briefy.leica import models
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils import types

revision = '90177ad0654d'
down_revision = 'c23e9aee0ca6'
branch_labels = None
depends_on = None


INSERTS_ITEMS_METADATA_TYPE = '''
INSERT INTO items (id, path, type, can_view, {fields}, state_history)
SELECT id, ARRAY[id], {table}.type, ARRAY[''], {fields}, state_history
from {table};
'''

INSERTS_ITEMS_METADATA = '''
INSERT INTO items (id, path, type, can_view, {fields}, state_history)
SELECT id, ARRAY[id], '{type}', ARRAY[''], {fields}, state_history
from {table};
'''

INSERTS_ITEMS_VERSIONS_TYPE = '''
INSERT INTO items_version (
id, path, type, can_view, transaction_id, end_transaction_id, operation_type, {fields}
)
SELECT id, ARRAY[id], type, ARRAY[''],
transaction_id, end_transaction_id, operation_type, {fields}
from {table}_version;
'''

INSERTS_ITEMS_VERSIONS = '''
INSERT INTO items_version (
id, path, type, can_view, transaction_id, end_transaction_id, operation_type, {fields}
)
SELECT id, ARRAY[id], '{type}', ARRAY[''],
transaction_id, end_transaction_id, operation_type, {fields}
from {table}_version;
'''

METADATA_MAP_TYPE = {
    'assets': 'title, slug, description, updated_at, created_at, state',
    'orders': 'title, slug, description, updated_at, created_at, state',
    'userprofiles': 'slug, description, updated_at, created_at, state',
}

METADATA_MAP = {
    'customers': 'title, slug, description, updated_at, created_at, state',
    'pools': 'title, slug, description, updated_at, created_at, state',
    'projects': 'title, slug, description, updated_at, created_at, state',
    'assignments': 'slug, updated_at, created_at, state',
}

INSERTS_LOCALROLES = '''
INSERT INTO localroles (id, item_id, item_type, principal_id, role_name, created_at, updated_at)
SELECT DISTINCT ON (entity_id, user_id, role_name)
   id, entity_id, '{item_type}', user_id, '{new_role_name}', created_at, updated_at
from localroles_deprecated
where role_name='{old_role_name}' AND entity_type='{old_item_type}'
order by entity_id, user_id, role_name;
'''

DROP_VIEWS = '''
DROP VIEW IF EXISTS orders_history_last_day;
DROP VIEW IF EXISTS orders_history_last_month;
DROP VIEW IF EXISTS orders_history;
'''


def rename_tables():
    """Rename tables."""
    op.rename_table('localroles', 'localroles_deprecated')
    op.rename_table('briefyuserprofiles', 'internaluserprofiles')
    op.rename_table('briefyuserprofiles_version', 'internaluserprofiles_version')


def drop_views():
    """Drop views."""
    op.execute(DROP_VIEWS)


def drop_columns():
    """Drop columns."""
    # assets
    op.drop_column('assets', 'description')
    op.drop_column('assets', 'updated_at')
    op.drop_column('assets', 'slug')
    op.drop_column('assets', 'state_history')
    op.drop_column('assets', 'state')
    op.drop_column('assets', 'type')
    op.drop_column('assets', 'created_at')
    op.drop_column('assets', 'title')

    # assets_version
    op.drop_column('assets_version', 'description')
    op.drop_column('assets_version', 'updated_at')
    op.drop_column('assets_version', 'slug')
    op.drop_column('assets_version', 'state')
    op.drop_column('assets_version', 'type')
    op.drop_column('assets_version', 'created_at')
    op.drop_column('assets_version', 'title')

    # assignments
    op.drop_column('assignments', 'updated_at')
    op.drop_column('assignments', 'slug')
    op.drop_column('assignments', 'state_history')
    op.drop_column('assignments', 'state')
    op.drop_column('assignments', 'created_at')

    # assignments_version
    op.drop_column('assignments_version', 'slug')
    op.drop_column('assignments_version', 'updated_at')
    op.drop_column('assignments_version', 'created_at')
    op.drop_column('assignments_version', 'state')

    # customers
    op.drop_column('customers', 'description')
    op.drop_column('customers', 'updated_at')
    op.drop_column('customers', 'slug')
    op.drop_column('customers', 'state_history')
    op.drop_column('customers', 'state')
    op.drop_column('customers', 'external_id')
    op.drop_column('customers', 'created_at')
    op.drop_column('customers', 'title')

    # remove deprecated fields
    op.drop_column('customers', 'tax_id_type')
    op.drop_column('customers', 'tax_id')
    op.drop_column('customers', 'tax_country')
    op.drop_column('customers', 'legal_name')
    op.drop_column('customers_version', 'tax_id_type')
    op.drop_column('customers_version', 'tax_id')
    op.drop_column('customers_version', 'tax_country')
    op.drop_column('customers_version', 'legal_name')

    # customers_version
    op.drop_column('customers_version', 'description')
    op.drop_column('customers_version', 'updated_at')
    op.drop_column('customers_version', 'slug')
    op.drop_column('customers_version', 'state')
    op.drop_column('customers_version', 'external_id')
    op.drop_column('customers_version', 'created_at')
    op.drop_column('customers_version', 'title')

    # orders
    op.drop_column('orders', 'description')
    op.drop_column('orders', 'updated_at')
    op.drop_column('orders', 'state_history')
    op.drop_column('orders', 'slug')
    op.drop_column('orders', 'state')
    op.drop_column('orders', 'type')
    op.drop_column('orders', 'external_id')
    op.drop_column('orders', 'created_at')
    op.drop_column('orders', 'title')

    # orders_version
    op.drop_column('orders_version', 'description')
    op.drop_column('orders_version', 'updated_at')
    op.drop_column('orders_version', 'slug')
    op.drop_column('orders_version', 'state')
    op.drop_column('orders_version', 'type'),
    op.drop_column('orders_version', 'external_id')
    op.drop_column('orders_version', 'created_at')
    op.drop_column('orders_version', 'title')

    # pools
    op.drop_column('pools', 'description')
    op.drop_column('pools', 'updated_at')
    op.drop_column('pools', 'slug')
    op.drop_column('pools', 'state_history')
    op.drop_column('pools', 'state')
    op.drop_column('pools', 'external_id')
    op.drop_column('pools', 'created_at')
    op.drop_column('pools', 'title')

    # pools_version
    op.drop_column('pools_version', 'description')
    op.drop_column('pools_version', 'updated_at')
    op.drop_column('pools_version', 'slug')
    op.drop_column('pools_version', 'state')
    op.drop_column('pools_version', 'external_id')
    op.drop_column('pools_version', 'created_at')
    op.drop_column('pools_version', 'title')

    # projects
    op.drop_column('projects', 'description')
    op.drop_column('projects', 'updated_at')
    op.drop_column('projects', 'slug')
    op.drop_column('projects', 'state_history')
    op.drop_column('projects', 'state')
    op.drop_column('projects', 'external_id')
    op.drop_column('projects', 'created_at')
    op.drop_column('projects', 'title')

    # projects_version
    op.drop_column('projects_version', 'description')
    op.drop_column('projects_version', 'updated_at')
    op.drop_column('projects_version', 'slug')
    op.drop_column('projects_version', 'state')
    op.drop_column('projects_version', 'external_id')
    op.drop_column('projects_version', 'created_at')
    op.drop_column('projects_version', 'title')

    # userprofiles
    op.drop_column('userprofiles', 'updated_at')
    op.drop_column('userprofiles', 'slug')
    op.drop_column('userprofiles', 'state_history')
    op.drop_column('userprofiles', 'state')
    op.drop_column('userprofiles', 'type')
    op.drop_column('userprofiles', 'external_id')
    op.drop_column('userprofiles', 'created_at')

    # userprofiles_version
    op.drop_column('userprofiles_version', 'updated_at')
    op.drop_column('userprofiles_version', 'slug')
    op.drop_column('userprofiles_version', 'state')
    op.drop_column('userprofiles_version', 'type')
    op.drop_column('userprofiles_version', 'external_id')
    op.drop_column('userprofiles_version', 'created_at')


def drop_indexes():
    """Drop old indexes."""
    # briefyuserprofiles before the rename to internaluserprofiles
    op.drop_index('ix_briefyuserprofiles_id', 'briefyuserprofiles')

    # briefyuserprofiles_version before the rename to internaluserprofiles_version
    op.drop_index('ix_briefyuserprofiles_version_end_transaction_id', 'briefyuserprofiles_version')
    op.drop_index('ix_briefyuserprofiles_version_id', 'briefyuserprofiles_version')
    op.drop_index('ix_briefyuserprofiles_version_operation_type', 'briefyuserprofiles_version')
    op.drop_index('ix_briefyuserprofiles_version_transaction_id', 'briefyuserprofiles_version')

    # localroles before the rename to localroles_deprecated
    op.drop_index('ix_localroles_can_create', 'localroles')
    op.drop_index('ix_localroles_can_delete', 'localroles')
    op.drop_index('ix_localroles_can_edit', 'localroles')
    op.drop_index('ix_localroles_can_list', 'localroles')
    op.drop_index('ix_localroles_can_view', 'localroles')
    op.drop_index('ix_localroles_created_at', 'localroles')
    op.drop_index('ix_localroles_entity_id', 'localroles')
    op.drop_index('ix_localroles_entity_type', 'localroles')
    op.drop_index('ix_localroles_role_name', 'localroles')
    op.drop_index('ix_localroles_updated_at', 'localroles')
    op.drop_index('ix_localroles_user_id', 'localroles')

    # assets
    op.drop_index('ix_assets_created_at', table_name='assets')
    op.drop_index('ix_assets_slug', table_name='assets')
    op.drop_index('ix_assets_title', table_name='assets')
    op.drop_index('ix_assets_updated_at', table_name='assets')

    # assets_version
    op.drop_index('ix_assets_version_created_at', table_name='assets_version')
    op.drop_index('ix_assets_version_slug', table_name='assets_version')
    op.drop_index('ix_assets_version_title', table_name='assets_version')
    op.drop_index('ix_assets_version_updated_at', table_name='assets_version')

    # assignments
    op.drop_index('ix_assignments_created_at', table_name='assignments')
    op.drop_index('ix_assignments_slug', table_name='assignments')
    op.drop_index('ix_assignments_updated_at', table_name='assignments')

    # assignments_version
    op.drop_index('ix_assignments_version_created_at', table_name='assignments_version')
    op.drop_index('ix_assignments_version_slug', table_name='assignments_version')
    op.drop_index('ix_assignments_version_updated_at', table_name='assignments_version')

    # customers
    op.drop_index('ix_customers_created_at', table_name='customers')
    op.drop_index('ix_customers_slug', table_name='customers')
    op.drop_index('ix_customers_title', table_name='customers')
    op.drop_index('ix_customers_updated_at', table_name='customers')

    # customers_version
    op.drop_index('ix_customers_version_created_at', table_name='customers_version')
    op.drop_index('ix_customers_version_slug', table_name='customers_version')
    op.drop_index('ix_customers_version_title', table_name='customers_version')
    op.drop_index('ix_customers_version_updated_at', table_name='customers_version')

    # orders
    op.drop_index('ix_orders_created_at', table_name='orders')
    op.drop_index('ix_orders_title', table_name='orders')
    op.drop_index('ix_orders_updated_at', table_name='orders')

    # orders_version
    op.drop_index('ix_orders_version_created_at', table_name='orders_version')
    op.drop_index('ix_orders_version_title', table_name='orders_version')
    op.drop_index('ix_orders_version_updated_at', table_name='orders_version')

    # pools
    op.drop_index('ix_pools_created_at', table_name='pools')
    op.drop_index('ix_pools_slug', table_name='pools')
    op.drop_index('ix_pools_title', table_name='pools')
    op.drop_index('ix_pools_updated_at', table_name='pools')

    # pools_version
    op.drop_index('ix_pools_version_created_at', table_name='pools_version')
    op.drop_index('ix_pools_version_slug', table_name='pools_version')
    op.drop_index('ix_pools_version_title', table_name='pools_version')
    op.drop_index('ix_pools_version_updated_at', table_name='pools_version')

    # projects
    op.drop_index('ix_projects_created_at', table_name='projects')
    op.drop_index('ix_projects_slug', table_name='projects')
    op.drop_index('ix_projects_title', table_name='projects')
    op.drop_index('ix_projects_updated_at', table_name='projects')

    # projects_version
    op.drop_index('ix_projects_version_created_at', table_name='projects_version')
    op.drop_index('ix_projects_version_slug', table_name='projects_version')
    op.drop_index('ix_projects_version_title', table_name='projects_version')
    op.drop_index('ix_projects_version_updated_at', table_name='projects_version')

    # userprofiles
    op.drop_index('ix_userprofiles_created_at', table_name='userprofiles')
    op.drop_index('ix_userprofiles_slug', table_name='userprofiles')
    op.drop_index('ix_userprofiles_updated_at', table_name='userprofiles')

    # userprofiles_version
    op.drop_index('ix_userprofiles_version_created_at', table_name='userprofiles_version')
    op.drop_index('ix_userprofiles_version_slug', table_name='userprofiles_version')
    op.drop_index('ix_userprofiles_version_updated_at', table_name='userprofiles_version')


def create_indexes():
    """Create new indexes."""
    # localroles_deprecated
    op.create_index(op.f('ix_localroles_deprecated_can_create'), 'localroles_deprecated',
                    ['can_create'], unique=False)
    op.create_index(op.f('ix_localroles_deprecated_can_delete'), 'localroles_deprecated',
                    ['can_delete'], unique=False)
    op.create_index(op.f('ix_localroles_deprecated_can_edit'), 'localroles_deprecated',
                    ['can_edit'], unique=False)
    op.create_index(op.f('ix_localroles_deprecated_can_list'), 'localroles_deprecated',
                    ['can_list'], unique=False)
    op.create_index(op.f('ix_localroles_deprecated_can_view'), 'localroles_deprecated',
                    ['can_view'], unique=False)
    op.create_index(op.f('ix_localroles_deprecated_created_at'), 'localroles_deprecated',
                    ['created_at'], unique=False)
    op.create_index(op.f('ix_localroles_deprecated_entity_id'), 'localroles_deprecated',
                    ['entity_id'], unique=False)
    op.create_index(op.f('ix_localroles_deprecated_entity_type'), 'localroles_deprecated',
                    ['entity_type'], unique=False)
    op.create_index(op.f('ix_localroles_deprecated_role_name'), 'localroles_deprecated',
                    ['role_name'], unique=False)
    op.create_index(op.f('ix_localroles_deprecated_updated_at'), 'localroles_deprecated',
                    ['updated_at'], unique=False)
    op.create_index(op.f('ix_localroles_deprecated_user_id'), 'localroles_deprecated', ['user_id'],
                    unique=False)

    # internaluserprofiles
    op.create_index(op.f('ix_internaluserprofiles_id'), 'internaluserprofiles', ['id'], unique=True)

    # internaluserprofiles_version
    op.create_index(op.f('ix_internaluserprofiles_version_end_transaction_id'),
                    'internaluserprofiles_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_internaluserprofiles_version_id'), 'internaluserprofiles_version',
                    ['id'], unique=False)
    op.create_index(op.f('ix_internaluserprofiles_version_operation_type'),
                    'internaluserprofiles_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_internaluserprofiles_version_transaction_id'),
                    'internaluserprofiles_version', ['transaction_id'], unique=False)
    # items
    op.create_index(op.f('ix_items_created_at'), 'items', ['created_at'], unique=False)
    op.create_index(op.f('ix_items_slug'), 'items', ['slug'], unique=False)
    op.create_index(op.f('ix_items_title'), 'items', ['title'], unique=False)
    op.create_index(op.f('ix_items_path'), 'items', ['path'], unique=False)
    op.create_index(op.f('ix_items_type'), 'items', ['type'], unique=False)
    op.create_index(op.f('ix_items_state'), 'items', ['state'], unique=False)
    op.create_index(op.f('ix_items_updated_at'), 'items', ['updated_at'], unique=False)

    # items_version
    op.create_index(op.f('ix_items_version_created_at'), 'items_version', ['created_at'],
                    unique=False)
    op.create_index(op.f('ix_items_version_end_transaction_id'), 'items_version',
                    ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_items_version_operation_type'), 'items_version', ['operation_type'],
                    unique=False)
    op.create_index(op.f('ix_items_version_slug'), 'items_version', ['slug'], unique=False)
    op.create_index(op.f('ix_items_version_title'), 'items_version', ['title'], unique=False)
    op.create_index(op.f('ix_items_version_transaction_id'), 'items_version', ['transaction_id'],
                    unique=False)
    op.create_index(op.f('ix_items_version_updated_at'), 'items_version', ['updated_at'],
                    unique=False)
    op.create_index(op.f('ix_items_version_path'), 'items_version', ['path'], unique=False)
    op.create_index(op.f('ix_items_version_state'), 'items_version', ['state'], unique=False)
    op.create_index(op.f('ix_items_version_type'), 'items_version', ['type'], unique=False)

    # localroles
    op.create_index(op.f('ix_localroles_created_at'), 'localroles', ['created_at'], unique=False)
    op.create_index(op.f('ix_localroles_item_type'), 'localroles', ['item_type'], unique=False)
    op.create_index(op.f('ix_localroles_item_id'), 'localroles', ['item_id'], unique=False)
    op.create_index(
        op.f('ix_localroles_principal_id'), 'localroles', ['principal_id'], unique=False
    )
    op.create_index(op.f('ix_localroles_updated_at'), 'localroles', ['updated_at'], unique=False)
    op.create_index(op.f('ix_localroles_role_name'), 'localroles', ['role_name'], unique=False)

    # customeruserprofiles
    op.create_index(op.f('ix_customeruserprofiles_customer_id'), 'customeruserprofiles',
                    ['customer_id'], unique=False)

    # customeruserprofiles_version
    op.create_index(op.f('ix_customeruserprofiles_version_customer_id'),
                    'customeruserprofiles_version', ['customer_id'], unique=False)

    # billing_infos
    op.create_index(op.f('ix_billing_infos_title'), 'billing_infos', ['title'], unique=False)
    op.create_index(
        op.f('ix_billing_infos_version_title'), 'billing_infos_version', ['title'], unique=False
    )
    op.create_index(op.f('ix_billing_infos_state'), 'billing_infos', ['state'], unique=False)
    op.create_index(op.f('ix_billing_infos_version_state'), 'billing_infos_version', ['state'],
                    unique=False)

    # new indexes for workflow mixin subclasses
    op.create_index(op.f('ix_comments_state'), 'comments', ['state'], unique=False)
    op.create_index(op.f('ix_customerbillingaddresses_state'), 'customerbillingaddresses',
                    ['state'], unique=False)
    op.create_index(op.f('ix_customercontacts_state'), 'customercontacts', ['state'], unique=False)

    op.create_index(op.f('ix_links_state'), 'links', ['state'], unique=False)
    op.create_index(op.f('ix_orderlocations_state'), 'orderlocations', ['state'], unique=False)
    op.create_index(op.f('ix_orderlocations_version_state'), 'orderlocations_version', ['state'],
                    unique=False)
    op.create_index(op.f('ix_workinglocations_state'), 'workinglocations', ['state'], unique=False)


def create_columns():
    """Create and alter columns and constraints."""
    op.create_unique_constraint(None, 'items', ['id'])
    op.create_unique_constraint(None, 'localroles', ['id'])

    op.drop_constraint('professionals_in_pool_pool_id_fkey', 'professionals_in_pool',
                       type_='foreignkey')
    op.drop_constraint('professionals_in_pool_professional_id_fkey', 'professionals_in_pool',
                       type_='foreignkey')

    op.alter_column('customercontacts', 'title',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.add_column(
        'customeruserprofiles',
        sa.Column('customer_id', types.UUIDType(), nullable=True)
    )
    op.add_column(
        'assignments_version',
        sa.Column('timezone', types.TimezoneType(), autoincrement=False, nullable=True)
    )
    op.add_column(
        'customeruserprofiles_version',
        sa.Column('customer_id', types.UUIDType(), autoincrement=False, nullable=True)
    )
    op.add_column('professionals', sa.Column('external_id', sa.String(length=255), nullable=True))
    op.add_column('professionals_version',
                  sa.Column('external_id', sa.String(length=255), autoincrement=False,
                            nullable=True))

    # fks to parent table items
    op.create_foreign_key(None, 'assets', 'items', ['id'], ['id'])
    op.create_foreign_key(None, 'assignments', 'items', ['id'], ['id'])
    op.create_foreign_key(None, 'customers', 'items', ['id'], ['id'])
    op.create_foreign_key(None, 'projects', 'items', ['id'], ['id'])
    op.create_foreign_key(None, 'userprofiles', 'items', ['id'], ['id'])
    op.create_foreign_key(None, 'orders', 'items', ['id'], ['id'])
    op.create_foreign_key(None, 'pools', 'items', ['id'], ['id'])

    # new fks
    op.create_foreign_key(None, 'localroles', 'items', ['item_id'], ['id'])
    op.create_foreign_key(None, 'customeruserprofiles', 'customers', ['customer_id'], ['id'])
    op.create_foreign_key(None, 'professionals_in_pool', 'professionals', ['professional_id'],
                          ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'professionals_in_pool', 'pools', ['pool_id'], ['id'],
                          ondelete='CASCADE')


def create_tables():
    """Create new tables."""
    op.create_table(
        'items',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('can_view', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(),
                  nullable=True),
        sa.Column('path', postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
                  nullable=False),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )

    op.create_table(
        'items_version',
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('can_view', postgresql.ARRAY(sa.String()), autoincrement=False,
                  nullable=True),
        sa.Column('title', sa.String(), autoincrement=False, nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('path', postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
                  autoincrement=False, nullable=True),
        sa.Column('type', sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False,
                  nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )

    op.create_table(
        'localroles',
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('item_type', sa.String(length=255), nullable=False),
        sa.Column('item_id', types.UUIDType(), sa.ForeignKey('items.id'), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('role_name', sa.String(255), nullable=False),
        sa.Column('item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('principal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )


def copy_metadata_items():
    """Copy base metadata fields from all tables to items table."""
    for table, fields in METADATA_MAP.items():
        insert = INSERTS_ITEMS_METADATA.format(
            table=table,
            fields=fields,
            type=table[:-1],
        )
        op.execute(insert)

    for table, fields in METADATA_MAP_TYPE.items():
        insert = INSERTS_ITEMS_METADATA_TYPE.format(
            table=table,
            fields=fields,
        )
        op.execute(insert)


def copy_versions_items():
    """Copy versions info from all tables to items_versions table."""
    for table, fields in METADATA_MAP.items():
        insert = INSERTS_ITEMS_VERSIONS.format(
            table=table,
            fields=fields,
            type=table[:-1],
        )
        op.execute(insert)

    for table, fields in METADATA_MAP_TYPE.items():
        insert = INSERTS_ITEMS_VERSIONS_TYPE.format(
            table=table,
            fields=fields,
        )
        op.execute(insert)


def update_type_internaluserprofile():
    """Update items.type from briefyuserprofile to internluserprofile."""
    op.execute("UPDATE items SET type='internaluserprofile' where type='briefyuserprofile'")


def copy_userprofiles_external_id():
    """Copy external_id from userprofiles to professionals table where type is professionals."""
    op.execute(
        '''
        UPDATE professionals SET external_id=other.external_id
        from 
        (SELECT id, external_id from userprofiles  WHERE type='professionals') as other 
        WHERE professionals.id=other.id
        '''
    )


def update_items_title_from_userprofiles():
    op.execute(
        '''
        UPDATE items SET title=other.title
        from
        (SELECT id, first_name || ' ' || last_name as title from userprofiles) as other
        WHERE items.id = other.id;
        '''
    )


def migrate_localroles():
    """Migration of localroles from the old table to the new one."""
    type_roles_mappping = {
        'customer': (
            ('account_manager', 'internal_account', 'Customer'),
            ('customer_user', 'customer_pm', 'Customer'),
        ),
        'project': (
            ('project_manager', 'internal_pm', 'Project'),
            ('customer_user', 'project_customer_pm', 'Project'),
        ),
        'assignment': (
            ('qa_manager', 'assignment_internal_scout', 'Assignment'),
            ('scout_manager', 'assignment_internal_qa', 'Assignment'),
            ('professional_user', 'professional_user', 'Assignment')
        ),
        'userprofile': (
            ('owner', 'owner', 'UserProfile'),
        ),
    }
    inserts = []
    for item_type, roles_mapping in type_roles_mappping.items():
        for role in roles_mapping:
            old_role_name, new_role_name, old_item_type = role
            inserts.append(
                INSERTS_LOCALROLES.format(
                    item_type=item_type,
                    old_role_name=old_role_name,
                    new_role_name=new_role_name,
                    old_item_type=old_item_type
                )
            )
    stmt = ''.join(inserts)
    op.execute(stmt)

    # now we need to update UserProfile type to correct type: Professional,

    # IMPORTANT 1: before this you need to enable pgcrypto extension in the leica database
    # this extensions is already enable on stg and live databases
    # to enable in your local database do:
    # $ psql -h localhost -p 9999 -U briefy briefy-leica
    # briefy-leica=# create extension pgcrypto;
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')

    # IMPORTANT 2: this query will take some time to run
    insert_qa_scout_roles = '''
    INSERT INTO localroles (id, item_id, item_type, principal_id, role_name, updated_at, created_at)
    SELECT
    gen_random_uuid() as id,
    item_id,
    item_type,
    principal_id,
    role_name,
    now() as updated_at,
    now() as created_at
    FROM
    (SELECT DISTINCT
    p.id as item_id,
    'project' as item_type,
    l.user_id as principal_id,
    CASE l.role_name
        WHEN 'qa_manager' THEN 'internal_qa'
        WHEN 'scout_manager' THEN 'internal_scout'
    END as role_name
    FROM projects as p, localroles_deprecated as l
    where l.role_name IN ('qa_manager', 'scout_manager')
    AND l.entity_id IN (
        SELECT a.id from assignments as a
        join orders as o on o.id=a.order_id
        where o.project_id = p.id)
    ORDER BY p.id) as source
    '''
    # disable this to run manually after since it's not mandatory
    # op.execute(insert_qa_scout_roles)

    add_missing_owner_local_roles = '''
    INSERT INTO localroles (id, item_id, item_type, principal_id, role_name, updated_at, created_at)
    SELECT
    gen_random_uuid() as id,
    source.item_id,
    'userprofile' as item_type,
    source.item_id as principal_id,
    'owner' as role_name,
    now() as updated_at,
    now() as created_at
    FROM
    (SELECT id as item_id FROM professionals
    WHERE id NOT IN (
    select item_id FROM localroles as l
    JOIN professionals as p
    on l.item_id = p.id
    WHERE l.role_name='owner')) as source
    '''
    op.execute(add_missing_owner_local_roles)


def update_items_path():
    """Update items.path column with data from the parent models."""
    update_sql = '''
    UPDATE items SET path=source.new_path
    from (
        SELECT DISTINCT
        items.id,
        array_cat(parent.path, ARRAY[items.id]) as new_path
        from {table}
        JOIN items on {table}.id = items.id
        JOIN (select id, path from items where items.type IN ({parent_types})) as parent
        on parent.id = {table}.{parent_attr}
        WHERE items.type IN ({item_types})
    ) as source
    WHERE items.type IN ({item_types}) AND source.id=items.id
    '''
    update_map = (
        ('projects', ("'customer'",), 'customer_id', ("'project'",)),
        ('orders', ("'project'",), 'project_id', ("'order'", "'leadorder'",)),
        ('assignments', ("'order'", "'leadorder'",), 'order_id', ("'assignment'",)),
    )
    for update_data in update_map:
        table, parent_types, parent_attr, item_types = update_data
        update = update_sql.format(
            table=table,
            item_types=','.join(item_types),
            parent_types=','.join(parent_types),
            parent_attr=parent_attr
        )
        op.execute(update)


def update_items_can_view():
    """Update items.can_view with default values."""
    can_view_update_map = (
        (models.Customer, ("'customer'",)),
        (models.Project, ("'project'",)),
        (models.Order, ("'order'", "'leadorder'")),
        (models.Assignment, ("'assignment'",)),
        (models.UserProfile, ("'customeruserprofile'", "'internaluserprofile'", "'professional'")),
    )

    for model, types in can_view_update_map:
        update = '''
        UPDATE items SET can_view=ARRAY[{roles}]
        WHERE items.type IN ({types})
        '''.format(
            roles=",".join(["'{0}'".format(r) for r in model._default_can_view()]),
            types=",".join(types)
        )

        op.execute(update)


def update_customeruserprofile():
    """Update customer_id attribute of CustomerUserProfile using Customer local roles."""
    update_sql = '''UPDATE customeruserprofiles SET customer_id=source.customer_id
    from (
        SELECT DISTINCT
        item_id as customer_id,
        principal_id
        FROM localroles
        WHERE localroles.item_type = 'customer'
    ) as source
    WHERE customeruserprofiles.id=source.principal_id
    '''
    op.execute(update_sql)


def alter_table_json_to_jsonb():
    """Alter all tables with json fields to jsonb."""
    alter_table_map = {
        'items': ['state_history'],
        'comments': ['state_history'],
        'links': ['state_history'],
        'customercontacts': ['state_history'],
        'customerbillingaddresses': ['state_history', 'info'],
        'orderlocations': ['state_history', 'info'],
        'assets': ['raw_metadata', 'history'],
        'assets_version': ['raw_metadata', 'history'],
        'projects': ['tech_requirements', 'delivery'],
        'orders': ['availability', 'delivery'],
        'billing_infos': ['state_history'],
    }

    for table, values in alter_table_map.items():
        for column in values:
            alter_table_template = f'''
                ALTER TABLE {table}
                ALTER COLUMN {column}
                SET DATA TYPE jsonb
                USING {column}::jsonb;
            '''
            op.execute(alter_table_template)


def upgrade():
    """Upgrade database."""
    print(revision)
    print('Drop views')
    drop_views()
    print('Drop indexes')
    drop_indexes()
    print('Rename tables')
    rename_tables()
    print('Create tables')
    create_tables()
    print('Copy metadata')
    copy_metadata_items()
    print('Copy versions')
    copy_versions_items()
    print('Create columns')
    create_columns()
    print('Create indexes')
    create_indexes()
    print('Update Internal User Profile')
    update_type_internaluserprofile()
    print('Update Items title from User Profile')
    update_items_title_from_userprofiles()
    print('Update User Profile external ID')
    copy_userprofiles_external_id()
    print('Migrate local roles')
    migrate_localroles()
    print('Update customer user profile')
    update_customeruserprofile()
    print('Update items path')
    update_items_path()
    print('Update items can_view')
    update_items_can_view()
    print('Alter tables with json fields to jsonb')
    alter_table_json_to_jsonb()
    print('Drop columns')
    drop_columns()


def downgrade():
    """Downgrade database model."""
    # no downgrade for this migration
    pass
