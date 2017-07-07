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
    op.drop_column('orders', 'external_id')
    op.drop_column('orders', 'created_at')
    op.drop_column('orders', 'title')

    # orders_version
    op.drop_column('orders_version', 'description')
    op.drop_column('orders_version', 'updated_at')
    op.drop_column('orders_version', 'state')
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


def create_columns():
    """Create new columns."""
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
    op.add_column('professionals_in_pool', sa.Column('id', types.UUIDType(), nullable=False))
    op.add_column('professionals_in_pool_version',
                  sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False))
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
        sa.Column('item_id', types.UUIDType(), sa.ForeignKey('items.id'), nullable=False),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('role_name', sa.String(255), nullable=False),
        sa.Column('item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('principal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )


def upgrade():
    """Upgrade database model."""
    drop_indexes()
    rename_tables()
    create_tables()
    create_columns()
    create_indexes()
    # TODO:
    # migrate data
    drop_columns()
    # drop tables


def downgrade():
    """Downgrade database model."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('userprofiles_version',
                  sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('userprofiles_version',
                  sa.Column('external_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('userprofiles_version',
                  sa.Column('type', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('userprofiles_version',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('userprofiles_version',
                  sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('userprofiles_version',
                  sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.create_index('ix_userprofiles_version_updated_at', 'userprofiles_version', ['updated_at'],
                    unique=False)
    op.create_index('ix_userprofiles_version_slug', 'userprofiles_version', ['slug'], unique=False)
    op.create_index('ix_userprofiles_version_created_at', 'userprofiles_version', ['created_at'],
                    unique=False)
    op.add_column('userprofiles',
                  sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('userprofiles',
                  sa.Column('external_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('userprofiles',
                  sa.Column('type', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('userprofiles',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('userprofiles', sa.Column('state_history', postgresql.JSON(astext_type=sa.Text()),
                                            autoincrement=False, nullable=True))
    op.add_column('userprofiles',
                  sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('userprofiles',
                  sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.drop_constraint(None, 'userprofiles', type_='foreignkey')
    op.create_index('ix_userprofiles_updated_at', 'userprofiles', ['updated_at'], unique=False)
    op.create_index('ix_userprofiles_slug', 'userprofiles', ['slug'], unique=False)
    op.create_index('ix_userprofiles_created_at', 'userprofiles', ['created_at'], unique=False)
    op.add_column('projects_version',
                  sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('projects_version',
                  sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('projects_version',
                  sa.Column('external_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('projects_version',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('projects_version',
                  sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('projects_version',
                  sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('projects_version',
                  sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.create_index('ix_projects_version_updated_at', 'projects_version', ['updated_at'],
                    unique=False)
    op.create_index('ix_projects_version_title', 'projects_version', ['title'], unique=False)
    op.create_index('ix_projects_version_slug', 'projects_version', ['slug'], unique=False)
    op.create_index('ix_projects_version_created_at', 'projects_version', ['created_at'],
                    unique=False)
    op.add_column('projects', sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('projects', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                                        nullable=True))
    op.add_column('projects',
                  sa.Column('external_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('projects',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('projects', sa.Column('state_history', postgresql.JSON(astext_type=sa.Text()),
                                        autoincrement=False, nullable=True))
    op.add_column('projects',
                  sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('projects', sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                                        nullable=True))
    op.add_column('projects',
                  sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'projects', type_='foreignkey')
    op.create_index('ix_projects_updated_at', 'projects', ['updated_at'], unique=False)
    op.create_index('ix_projects_title', 'projects', ['title'], unique=False)
    op.create_index('ix_projects_slug', 'projects', ['slug'], unique=False)
    op.create_index('ix_projects_created_at', 'projects', ['created_at'], unique=False)
    op.drop_column('professionals_version', 'external_id')
    op.drop_column('professionals_in_pool_version', 'id')
    op.drop_constraint(None, 'professionals_in_pool', type_='foreignkey')
    op.drop_constraint(None, 'professionals_in_pool', type_='foreignkey')
    op.create_foreign_key('professionals_in_pool_professional_id_fkey', 'professionals_in_pool',
                          'professionals', ['professional_id'], ['id'])
    op.create_foreign_key('professionals_in_pool_pool_id_fkey', 'professionals_in_pool', 'pools',
                          ['pool_id'], ['id'])
    op.drop_constraint(None, 'professionals_in_pool', type_='unique')
    op.drop_column('professionals_in_pool', 'id')
    op.drop_column('professionals', 'external_id')
    op.add_column('pools_version',
                  sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('pools_version',
                  sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('pools_version',
                  sa.Column('external_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('pools_version',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('pools_version',
                  sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('pools_version',
                  sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('pools_version',
                  sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.create_index('ix_pools_version_updated_at', 'pools_version', ['updated_at'], unique=False)
    op.create_index('ix_pools_version_title', 'pools_version', ['title'], unique=False)
    op.create_index('ix_pools_version_slug', 'pools_version', ['slug'], unique=False)
    op.create_index('ix_pools_version_created_at', 'pools_version', ['created_at'], unique=False)
    op.add_column('pools', sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('pools', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                                     nullable=True))
    op.add_column('pools',
                  sa.Column('external_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('pools',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('pools', sa.Column('state_history', postgresql.JSON(astext_type=sa.Text()),
                                     autoincrement=False, nullable=True))
    op.add_column('pools',
                  sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('pools', sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                                     nullable=True))
    op.add_column('pools', sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'pools', type_='foreignkey')
    op.create_index('ix_pools_updated_at', 'pools', ['updated_at'], unique=False)
    op.create_index('ix_pools_title', 'pools', ['title'], unique=False)
    op.create_index('ix_pools_slug', 'pools', ['slug'], unique=False)
    op.create_index('ix_pools_created_at', 'pools', ['created_at'], unique=False)
    op.add_column('orders_version',
                  sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('orders_version',
                  sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('orders_version',
                  sa.Column('external_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('orders_version',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('orders_version',
                  sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('orders_version',
                  sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.create_index('ix_orders_version_updated_at', 'orders_version', ['updated_at'], unique=False)
    op.create_index('ix_orders_version_title', 'orders_version', ['title'], unique=False)
    op.create_index('ix_orders_version_created_at', 'orders_version', ['created_at'], unique=False)
    op.add_column('orders', sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('orders', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                                      nullable=True))
    op.add_column('orders',
                  sa.Column('external_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('orders',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('orders', sa.Column('state_history', postgresql.JSON(astext_type=sa.Text()),
                                      autoincrement=False, nullable=True))
    op.add_column('orders', sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                                      nullable=True))
    op.add_column('orders', sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'orders', type_='foreignkey')
    op.create_index('ix_orders_updated_at', 'orders', ['updated_at'], unique=False)
    op.create_index('ix_orders_title', 'orders', ['title'], unique=False)
    op.create_index('ix_orders_created_at', 'orders', ['created_at'], unique=False)
    op.add_column('localroles',
                  sa.Column('entity_type', sa.VARCHAR(length=255), autoincrement=False,
                            nullable=False))
    op.add_column('localroles',
                  sa.Column('can_list', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('localroles',
                  sa.Column('entity_id', postgresql.UUID(), autoincrement=False, nullable=False))
    op.add_column('localroles',
                  sa.Column('can_create', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('localroles',
                  sa.Column('user_id', postgresql.UUID(), autoincrement=False, nullable=False))
    op.add_column('localroles',
                  sa.Column('can_view', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('localroles',
                  sa.Column('can_edit', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('localroles',
                  sa.Column('can_delete', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'localroles', type_='foreignkey')
    op.create_index('ix_localroles_user_id', 'localroles', ['user_id'], unique=False)
    op.create_index('ix_localroles_role_name', 'localroles', ['role_name'], unique=False)
    op.create_index('ix_localroles_entity_type', 'localroles', ['entity_type'], unique=False)
    op.create_index('ix_localroles_entity_id', 'localroles', ['entity_id'], unique=False)
    op.create_index('ix_localroles_can_view', 'localroles', ['can_view'], unique=False)
    op.create_index('ix_localroles_can_list', 'localroles', ['can_list'], unique=False)
    op.create_index('ix_localroles_can_edit', 'localroles', ['can_edit'], unique=False)
    op.create_index('ix_localroles_can_delete', 'localroles', ['can_delete'], unique=False)
    op.create_index('ix_localroles_can_create', 'localroles', ['can_create'], unique=False)
    op.drop_column('localroles', 'principal_id')
    op.drop_column('localroles', 'item_id')
    op.drop_index(op.f('ix_customeruserprofiles_version_customer_id'),
                  table_name='customeruserprofiles_version')
    op.drop_column('customeruserprofiles_version', 'customer_id')
    op.drop_constraint(None, 'customeruserprofiles', type_='foreignkey')
    op.drop_index(op.f('ix_customeruserprofiles_customer_id'), table_name='customeruserprofiles')
    op.drop_column('customeruserprofiles', 'customer_id')
    op.add_column('customers_version',
                  sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('customers_version',
                  sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('customers_version',
                  sa.Column('external_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('customers_version',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('customers_version',
                  sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('customers_version',
                  sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('customers_version',
                  sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.create_index('ix_customers_version_updated_at', 'customers_version', ['updated_at'],
                    unique=False)
    op.create_index('ix_customers_version_title', 'customers_version', ['title'], unique=False)
    op.create_index('ix_customers_version_slug', 'customers_version', ['slug'], unique=False)
    op.create_index('ix_customers_version_created_at', 'customers_version', ['created_at'],
                    unique=False)
    op.add_column('customers',
                  sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('customers', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                                         nullable=True))
    op.add_column('customers',
                  sa.Column('external_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('customers',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('customers', sa.Column('state_history', postgresql.JSON(astext_type=sa.Text()),
                                         autoincrement=False, nullable=True))
    op.add_column('customers',
                  sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('customers', sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                                         nullable=True))
    op.add_column('customers',
                  sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'customers', type_='foreignkey')
    op.create_index('ix_customers_updated_at', 'customers', ['updated_at'], unique=False)
    op.create_index('ix_customers_title', 'customers', ['title'], unique=False)
    op.create_index('ix_customers_slug', 'customers', ['slug'], unique=False)
    op.create_index('ix_customers_created_at', 'customers', ['created_at'], unique=False)
    op.alter_column('customercontacts', 'title',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.add_column('assignments_version',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('assignments_version',
                  sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('assignments_version',
                  sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('assignments_version',
                  sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.create_index('ix_assignments_version_updated_at', 'assignments_version', ['updated_at'],
                    unique=False)
    op.create_index('ix_assignments_version_slug', 'assignments_version', ['slug'], unique=False)
    op.create_index('ix_assignments_version_created_at', 'assignments_version', ['created_at'],
                    unique=False)
    op.drop_column('assignments_version', 'timezone')
    op.add_column('assignments',
                  sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('assignments',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('assignments', sa.Column('state_history', postgresql.JSON(astext_type=sa.Text()),
                                           autoincrement=False, nullable=True))
    op.add_column('assignments',
                  sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('assignments',
                  sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.drop_constraint(None, 'assignments', type_='foreignkey')
    op.create_index('ix_assignments_updated_at', 'assignments', ['updated_at'], unique=False)
    op.create_index('ix_assignments_slug', 'assignments', ['slug'], unique=False)
    op.create_index('ix_assignments_created_at', 'assignments', ['created_at'], unique=False)
    op.add_column('assets_version',
                  sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('assets_version',
                  sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('assets_version',
                  sa.Column('type', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('assets_version',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('assets_version',
                  sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('assets_version',
                  sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                            nullable=True))
    op.add_column('assets_version',
                  sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.create_index('ix_assets_version_updated_at', 'assets_version', ['updated_at'], unique=False)
    op.create_index('ix_assets_version_title', 'assets_version', ['title'], unique=False)
    op.create_index('ix_assets_version_slug', 'assets_version', ['slug'], unique=False)
    op.create_index('ix_assets_version_created_at', 'assets_version', ['created_at'], unique=False)
    op.add_column('assets', sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('assets', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False,
                                      nullable=True))
    op.add_column('assets',
                  sa.Column('type', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.add_column('assets',
                  sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('assets', sa.Column('state_history', postgresql.JSON(astext_type=sa.Text()),
                                      autoincrement=False, nullable=True))
    op.add_column('assets',
                  sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('assets', sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False,
                                      nullable=True))
    op.add_column('assets', sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'assets', type_='foreignkey')
    op.create_index('ix_assets_updated_at', 'assets', ['updated_at'], unique=False)
    op.create_index('ix_assets_title', 'assets', ['title'], unique=False)
    op.create_index('ix_assets_slug', 'assets', ['slug'], unique=False)
    op.create_index('ix_assets_created_at', 'assets', ['created_at'], unique=False)
    op.create_table('briefyuserprofiles_version',
                    sa.Column('id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False,
                              nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('id', 'transaction_id',
                                            name='briefyuserprofiles_version_pkey')
                    )
    op.create_table('briefyuserprofiles',
                    sa.Column('id', postgresql.UUID(), autoincrement=False, nullable=False),
                    sa.ForeignKeyConstraint(['id'], ['userprofiles.id'],
                                            name='briefyuserprofiles_id_fkey'),
                    sa.PrimaryKeyConstraint('id', name='briefyuserprofiles_pkey')
                    )
    op.drop_index(op.f('ix_internaluserprofiles_id'), table_name='internaluserprofiles')
    op.drop_table('internaluserprofiles')
    op.drop_index(op.f('ix_localroles_deprecated_user_id'), table_name='localroles_deprecated')
    op.drop_index(op.f('ix_localroles_deprecated_updated_at'), table_name='localroles_deprecated')
    op.drop_index(op.f('ix_localroles_deprecated_role_name'), table_name='localroles_deprecated')
    op.drop_index(op.f('ix_localroles_deprecated_entity_type'), table_name='localroles_deprecated')
    op.drop_index(op.f('ix_localroles_deprecated_entity_id'), table_name='localroles_deprecated')
    op.drop_index(op.f('ix_localroles_deprecated_created_at'), table_name='localroles_deprecated')
    op.drop_index(op.f('ix_localroles_deprecated_can_view'), table_name='localroles_deprecated')
    op.drop_index(op.f('ix_localroles_deprecated_can_list'), table_name='localroles_deprecated')
    op.drop_index(op.f('ix_localroles_deprecated_can_edit'), table_name='localroles_deprecated')
    op.drop_index(op.f('ix_localroles_deprecated_can_delete'), table_name='localroles_deprecated')
    op.drop_index(op.f('ix_localroles_deprecated_can_create'), table_name='localroles_deprecated')
    op.drop_table('localroles_deprecated')
    op.drop_index(op.f('ix_items_version_updated_at'), table_name='items_version')
    op.drop_index(op.f('ix_items_version_transaction_id'), table_name='items_version')
    op.drop_index(op.f('ix_items_version_title'), table_name='items_version')
    op.drop_index(op.f('ix_items_version_slug'), table_name='items_version')
    op.drop_index(op.f('ix_items_version_operation_type'), table_name='items_version')
    op.drop_index(op.f('ix_items_version_end_transaction_id'), table_name='items_version')
    op.drop_index(op.f('ix_items_version_created_at'), table_name='items_version')
    op.drop_table('items_version')
    op.drop_index(op.f('ix_items_updated_at'), table_name='items')
    op.drop_index(op.f('ix_items_title'), table_name='items')
    op.drop_index(op.f('ix_items_slug'), table_name='items')
    op.drop_index(op.f('ix_items_created_at'), table_name='items')
    op.drop_table('items')
    op.drop_index(op.f('ix_internaluserprofiles_version_transaction_id'),
                  table_name='internaluserprofiles_version')
    op.drop_index(op.f('ix_internaluserprofiles_version_operation_type'),
                  table_name='internaluserprofiles_version')
    op.drop_index(op.f('ix_internaluserprofiles_version_id'),
                  table_name='internaluserprofiles_version')
    op.drop_index(op.f('ix_internaluserprofiles_version_end_transaction_id'),
                  table_name='internaluserprofiles_version')
    op.drop_table('internaluserprofiles_version')
    # ### end Alembic commands ###
