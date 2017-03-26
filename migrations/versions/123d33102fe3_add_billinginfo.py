"""Add BillingInfo.

Revision ID: 123d33102fe3
Revises: 60bc86209022
Create Date: 2017-03-21 17:08:45.413835
"""
from alembic import op
from briefy.common.db.types.aware_datetime import AwareDateTime
from briefy.leica.vocabularies import TaxIdTypes
from briefy.leica.vocabularies import TaxIdStatusCustomers
from briefy.leica.vocabularies import TaxIdStatusProfessionals
from sqlalchemy_utils import types
from sqlalchemy.dialects import postgresql

import sqlalchemy as sa
import sqlalchemy_utils

revision = '123d33102fe3'
down_revision = '60bc86209022'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.create_table(
        'billing_infos',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=False),
        sa.Column('last_name', sa.String(length=255), nullable=False),
        sa.Column('billing_address', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tax_id_type', types.ChoiceType(choices=TaxIdTypes, impl=sa.String(length=3)),
                  nullable=False),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('tax_id_name', sa.String(length=50), nullable=True),
        sa.Column('email', sqlalchemy_utils.types.email.EmailType(length=255), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_billing_infos_created_at'), 'billing_infos', ['created_at'],
                    unique=False)
    op.create_index(op.f('ix_billing_infos_slug'), 'billing_infos', ['slug'], unique=False)
    op.create_index(op.f('ix_billing_infos_title'), 'billing_infos', ['title'], unique=False)
    op.create_index(op.f('ix_billing_infos_updated_at'), 'billing_infos', ['updated_at'],
                    unique=False)
    op.create_table(
        'billing_infos_version',
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('first_name', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('last_name', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('billing_address', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False,
                  nullable=True),
        sa.Column('tax_id_type', types.ChoiceType(choices=TaxIdTypes, impl=sa.String(length=3)),
                  autoincrement=False, nullable=True),
        sa.Column('tax_id', sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column('tax_id_name', sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column('email', sqlalchemy_utils.types.email.EmailType(length=255), autoincrement=False,
                  nullable=True),
        sa.Column('type', sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_billing_infos_version_created_at'), 'billing_infos_version',
                    ['created_at'], unique=False)
    op.create_index(op.f('ix_billing_infos_version_end_transaction_id'), 'billing_infos_version',
                    ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_billing_infos_version_operation_type'), 'billing_infos_version',
                    ['operation_type'], unique=False)
    op.create_index(op.f('ix_billing_infos_version_slug'), 'billing_infos_version', ['slug'],
                    unique=False)
    op.create_index(op.f('ix_billing_infos_version_title'), 'billing_infos_version', ['title'],
                    unique=False)
    op.create_index(op.f('ix_billing_infos_version_transaction_id'), 'billing_infos_version',
                    ['transaction_id'], unique=False)
    op.create_index(op.f('ix_billing_infos_version_updated_at'), 'billing_infos_version',
                    ['updated_at'], unique=False)
    op.create_table(
        'customer_billing_infos_version',
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('customer_id', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('tax_id_status',
                  types.ChoiceType(choices=TaxIdStatusCustomers, impl=sa.String(length=3)),
                  autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_customer_billing_infos_version_customer_id'),
                    'customer_billing_infos_version', ['customer_id'], unique=False)
    op.create_index(op.f('ix_customer_billing_infos_version_end_transaction_id'),
                    'customer_billing_infos_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_customer_billing_infos_version_id'), 'customer_billing_infos_version',
                    ['id'], unique=False)
    op.create_index(op.f('ix_customer_billing_infos_version_operation_type'),
                    'customer_billing_infos_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_customer_billing_infos_version_transaction_id'),
                    'customer_billing_infos_version', ['transaction_id'], unique=False)
    op.create_table(
        'professional_billing_infos_version',
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('professional_id', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('tax_id_status',
                  types.ChoiceType(choices=TaxIdStatusProfessionals, impl=sa.String(length=3)),
                  autoincrement=False, nullable=True),
        sa.Column('payment_info', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False,
                  nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_professional_billing_infos_version_end_transaction_id'),
                    'professional_billing_infos_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_professional_billing_infos_version_id'),
                    'professional_billing_infos_version', ['id'], unique=False)
    op.create_index(op.f('ix_professional_billing_infos_version_operation_type'),
                    'professional_billing_infos_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_professional_billing_infos_version_professional_id'),
                    'professional_billing_infos_version', ['professional_id'], unique=False)
    op.create_index(op.f('ix_professional_billing_infos_version_transaction_id'),
                    'professional_billing_infos_version', ['transaction_id'], unique=False)
    op.create_table(
        'customer_billing_infos',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('customer_id', types.UUIDType(), nullable=True),
        sa.Column('tax_id_status',
                  types.ChoiceType(choices=TaxIdStatusCustomers, impl=sa.String(length=3)),
                  nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['id'], ['billing_infos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customer_billing_infos_customer_id'), 'customer_billing_infos',
                    ['customer_id'], unique=True)
    op.create_index(op.f('ix_customer_billing_infos_id'), 'customer_billing_infos', ['id'],
                    unique=True)
    op.create_table(
        'professional_billing_infos',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('professional_id', types.UUIDType(), nullable=True),
        sa.Column('tax_id_status',
                  types.ChoiceType(choices=TaxIdStatusProfessionals, impl=sa.String(length=3)),
                  nullable=True),
        sa.Column('payment_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['billing_infos.id'], ),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_professional_billing_infos_id'), 'professional_billing_infos', ['id'],
                    unique=True)
    op.create_index(op.f('ix_professional_billing_infos_professional_id'),
                    'professional_billing_infos', ['professional_id'], unique=True)


def downgrade():
    """Downgrade database model."""
    op.drop_index(op.f('ix_professional_billing_infos_professional_id'),
                  table_name='professional_billing_infos')
    op.drop_index(op.f('ix_professional_billing_infos_id'), table_name='professional_billing_infos')
    op.drop_table('professional_billing_infos')
    op.drop_index(op.f('ix_customer_billing_infos_id'), table_name='customer_billing_infos')
    op.drop_index(op.f('ix_customer_billing_infos_customer_id'),
                  table_name='customer_billing_infos')
    op.drop_table('customer_billing_infos')
    op.drop_index(op.f('ix_professional_billing_infos_version_transaction_id'),
                  table_name='professional_billing_infos_version')
    op.drop_index(op.f('ix_professional_billing_infos_version_professional_id'),
                  table_name='professional_billing_infos_version')
    op.drop_index(op.f('ix_professional_billing_infos_version_operation_type'),
                  table_name='professional_billing_infos_version')
    op.drop_index(op.f('ix_professional_billing_infos_version_id'),
                  table_name='professional_billing_infos_version')
    op.drop_index(op.f('ix_professional_billing_infos_version_end_transaction_id'),
                  table_name='professional_billing_infos_version')
    op.drop_table('professional_billing_infos_version')
    op.drop_index(op.f('ix_customer_billing_infos_version_transaction_id'),
                  table_name='customer_billing_infos_version')
    op.drop_index(op.f('ix_customer_billing_infos_version_operation_type'),
                  table_name='customer_billing_infos_version')
    op.drop_index(op.f('ix_customer_billing_infos_version_id'),
                  table_name='customer_billing_infos_version')
    op.drop_index(op.f('ix_customer_billing_infos_version_end_transaction_id'),
                  table_name='customer_billing_infos_version')
    op.drop_index(op.f('ix_customer_billing_infos_version_customer_id'),
                  table_name='customer_billing_infos_version')
    op.drop_table('customer_billing_infos_version')
    op.drop_index(op.f('ix_billing_infos_version_updated_at'), table_name='billing_infos_version')
    op.drop_index(op.f('ix_billing_infos_version_transaction_id'),
                  table_name='billing_infos_version')
    op.drop_index(op.f('ix_billing_infos_version_title'), table_name='billing_infos_version')
    op.drop_index(op.f('ix_billing_infos_version_slug'), table_name='billing_infos_version')
    op.drop_index(op.f('ix_billing_infos_version_operation_type'),
                  table_name='billing_infos_version')
    op.drop_index(op.f('ix_billing_infos_version_end_transaction_id'),
                  table_name='billing_infos_version')
    op.drop_index(op.f('ix_billing_infos_version_created_at'), table_name='billing_infos_version')
    op.drop_table('billing_infos_version')
    op.drop_index(op.f('ix_billing_infos_updated_at'), table_name='billing_infos')
    op.drop_index(op.f('ix_billing_infos_title'), table_name='billing_infos')
    op.drop_index(op.f('ix_billing_infos_slug'), table_name='billing_infos')
    op.drop_index(op.f('ix_billing_infos_created_at'), table_name='billing_infos')
    op.drop_table('billing_infos')
