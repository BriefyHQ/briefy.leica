"""Change permission model.

Revision ID: 90177ad0654d
Revises: cab6693525e6
Create Date: 2017-07-05 11:40:10.204660
"""
import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from briefy.common.db.types.aware_datetime import AwareDateTime
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils import types

revision = '90177ad0654d'
down_revision = 'cab6693525e6'
branch_labels = None
depends_on = None


INSERTS_ITEMS_METADATA_TYPE = '''
INSERT INTO items (id, path, type, can_view, {fields}, state_history)
SELECT id, ARRAY[id], type, ARRAY[''], {fields}, state_history
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
INSERT INTO localroles (id, item_id, item_type, principal_id, role_name)
SELECT id, entity_id, '{item_type}', user_id, '{new_role_name}'
from localroles_deprecated
where role_name='{old_role_name}' AND entity_type='{item_type}';
'''


def rename_tables():
    """Rename tables."""
    op.rename_table('localroles', 'localroles_deprecated')
    op.rename_table('briefyuserprofiles', 'internaluserprofiles')
    op.rename_table('briefyuserprofiles_version', 'internaluserprofiles_version')


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
    op.drop_column('customers_version', 'tax_id_type')
    op.drop_column('customers_version', 'tax_id')
    op.drop_column('customers_version', 'tax_country')

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
    op.drop_column('orders', 'state')
    op.drop_column('orders', 'type')
    op.drop_column('orders', 'external_id')
    op.drop_column('orders', 'created_at')
    op.drop_column('orders', 'title')

    # orders_version
    op.drop_column('orders_version', 'description')
    op.drop_column('orders_version', 'updated_at')
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
            type=table,
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
            type=table,
        )
        op.execute(insert)

    for table, fields in METADATA_MAP_TYPE.items():
        insert = INSERTS_ITEMS_VERSIONS_TYPE.format(
            table=table,
            fields=fields,
        )
        op.execute(insert)


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


def migrate_localroles():
    """Migration of localroles from the old table to the new one."""
    type_roles_mappping = {
        'Customer': (
            ('account_manager', 'internal_account', 'Customer'),
            ('customer_user', 'customer_pm', 'Customer'),
        ),
        'Project': (
            # TODO: add on Project using distinct values from children objects
            # ('qa_manager', 'internal_qa', 'Assignment'),
            # ('scout_manager', 'internal_scout', 'Order'),
            ('project_manager', 'internal_pm', 'Project'),
            ('customer_user', 'project_customer_pm', 'Project'),
        ),
        'Assignment': (
            ('qa_manager', 'assignment_internal_scout', 'Assignment'),
            ('scout_manager', 'assignment_internal_qa', 'Assignment'),
            ('professional_user', 'professional_user', 'Assignment')
        ),
    }

    for item_type, roles_mapping in type_roles_mappping.items():
        for role in roles_mapping:
            old_role_name, new_role_name, old_item_type = role
            insert = INSERTS_LOCALROLES.format(
                item_type=item_type,
                old_role_name=old_role_name,
                new_role_name=new_role_name
            )
            op.execute(insert)


def upgrade():
    """Upgrade database."""
    drop_indexes()
    rename_tables()
    create_tables()
    copy_metadata_items()
    copy_versions_items()
    create_columns()
    create_indexes()
    copy_userprofiles_external_id()
    migrate_localroles()
    drop_columns()


def downgrade():
    """Downgrade database model."""
    # no downgrade for this migration
    pass
