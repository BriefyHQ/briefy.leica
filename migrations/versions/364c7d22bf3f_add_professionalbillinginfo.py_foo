"""Add ProfessionalBillingInfo.

Revision ID: 364c7d22bf3f
Revises: 60bc86209022
Create Date: 2017-03-20 21:32:32.746120
"""
from alembic import op
from briefy.common.db.types.aware_datetime import AwareDateTime
from sqlalchemy_utils import types
from sqlalchemy.dialects import postgresql

import sqlalchemy as sa

revision = '364c7d22bf3f'
down_revision = '60bc86209022'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.create_table(
        'professional_billing_infos_version',
        sa.Column('id', types.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('slug', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('created_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('tax_id', sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column('tax_id_type', sa.String(length=50), autoincrement=False, nullable=True),
        sa.Column('tax_country', types.CountryType(length=2), autoincrement=False, nullable=True),
        sa.Column(
            'billing_address',
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False, nullable=True
        ),
        sa.Column('professional_id', types.UUIDType(), autoincrement=False, nullable=True),
        sa.Column('legal_name', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('first_name', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('last_name', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('email', types.EmailType(length=255), autoincrement=False, nullable=True),
        sa.Column(
            'payment_info',
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True
        ),
        sa.Column('updated_at', AwareDateTime(), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_professional_billing_infos_version_created_at'),
        'professional_billing_infos_version',
        ['created_at'],
        unique=False
    )
    op.create_index(
        op.f('ix_professional_billing_infos_version_end_transaction_id'),
        'professional_billing_infos_version', ['end_transaction_id'], unique=False)
    op.create_index(
        op.f('ix_professional_billing_infos_version_first_name'),
        'professional_billing_infos_version', ['first_name'], unique=False)
    op.create_index(
        op.f('ix_professional_billing_infos_version_last_name'),
        'professional_billing_infos_version', ['last_name'], unique=False)
    op.create_index(
        op.f('ix_professional_billing_infos_version_operation_type'),
        'professional_billing_infos_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_professional_billing_infos_version_professional_id'),
        'professional_billing_infos_version', ['professional_id'], unique=False)
    op.create_index(
        op.f('ix_professional_billing_infos_version_slug'),
        'professional_billing_infos_version', ['slug'], unique=False)
    op.create_index(
        op.f('ix_professional_billing_infos_version_transaction_id'),
        'professional_billing_infos_version', ['transaction_id'], unique=False)
    op.create_index(
        op.f('ix_professional_billing_infos_version_updated_at'),
        'professional_billing_infos_version', ['updated_at'], unique=False)
    op.create_table(
        'professional_billing_infos',
        sa.Column('id', types.UUIDType(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=True),
        sa.Column('created_at', AwareDateTime(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('state_history', types.JSONType(), nullable=True),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('tax_id_type', sa.String(length=50), nullable=True),
        sa.Column('tax_country', types.CountryType(length=2), nullable=True),
        sa.Column('billing_address', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('professional_id', types.UUIDType(), nullable=True),
        sa.Column('legal_name', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=False),
        sa.Column('last_name', sa.String(length=255), nullable=False),
        sa.Column('email', types.EmailType(length=255), nullable=True),
        sa.Column('payment_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('updated_at', AwareDateTime(), nullable=True),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('id')
    )
    op.create_index(
        op.f('ix_professional_billing_infos_created_at'), 'professional_billing_infos',
        ['created_at'], unique=False)
    op.create_index(
        op.f('ix_professional_billing_infos_first_name'), 'professional_billing_infos',
        ['first_name'], unique=False)
    op.create_index(
        op.f('ix_professional_billing_infos_last_name'), 'professional_billing_infos',
        ['last_name'], unique=False)
    op.create_index(
        op.f('ix_professional_billing_infos_professional_id'),
        'professional_billing_infos', ['professional_id'], unique=True)
    op.create_index(
        op.f('ix_professional_billing_infos_slug'), 'professional_billing_infos',
        ['slug'], unique=False)
    op.create_index(
        op.f('ix_professional_billing_infos_updated_at'),
        'professional_billing_infos',
        ['updated_at'], unique=False)


def downgrade():
    """Downgrade database model."""
    op.drop_index(op.f('ix_professional_billing_infos_updated_at'),
                  table_name='professional_billing_infos')
    op.drop_index(op.f('ix_professional_billing_infos_slug'),
                  table_name='professional_billing_infos')
    op.drop_index(op.f('ix_professional_billing_infos_professional_id'),
                  table_name='professional_billing_infos')
    op.drop_index(op.f('ix_professional_billing_infos_last_name'),
                  table_name='professional_billing_infos')
    op.drop_index(op.f('ix_professional_billing_infos_first_name'),
                  table_name='professional_billing_infos')
    op.drop_index(op.f('ix_professional_billing_infos_created_at'),
                  table_name='professional_billing_infos')
    op.drop_table('professional_billing_infos')
    op.drop_index(op.f('ix_professional_billing_infos_version_updated_at'),
                  table_name='professional_billing_infos_version')
    op.drop_index(op.f('ix_professional_billing_infos_version_transaction_id'),
                  table_name='professional_billing_infos_version')
    op.drop_index(op.f('ix_professional_billing_infos_version_slug'),
                  table_name='professional_billing_infos_version')
    op.drop_index(op.f('ix_professional_billing_infos_version_professional_id'),
                  table_name='professional_billing_infos_version')
    op.drop_index(op.f('ix_professional_billing_infos_version_operation_type'),
                  table_name='professional_billing_infos_version')
    op.drop_index(op.f('ix_professional_billing_infos_version_last_name'),
                  table_name='professional_billing_infos_version')
    op.drop_index(op.f('ix_professional_billing_infos_version_first_name'),
                  table_name='professional_billing_infos_version')
    op.drop_index(op.f('ix_professional_billing_infos_version_end_transaction_id'),
                  table_name='professional_billing_infos_version')
    op.drop_index(op.f('ix_professional_billing_infos_version_created_at'),
                  table_name='professional_billing_infos_version')
    op.drop_table('professional_billing_infos_version')
