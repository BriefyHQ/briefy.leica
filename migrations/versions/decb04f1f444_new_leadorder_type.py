"""New LeadOrder type..

Revision ID: decb04f1f444
Revises: bccb04f1f444
Create Date: 2017-05-22 18:00:41.524443
"""
from alembic import op
from sqlalchemy_utils import types


import sqlalchemy as sa


revision = 'decb04f1f444'
down_revision = 'bccb04f1f444'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    # Drop leadorder table
    op.drop_index(op.f('ix_leadorder_id'), table_name='leadorder')
    op.drop_table('leadorder')
    op.drop_index(op.f('ix_leadorder_version_transaction_id'), table_name='leadorder_version')
    op.drop_index(op.f('ix_leadorder_version_operation_type'), table_name='leadorder_version')
    op.drop_index(op.f('ix_leadorder_version_id'), table_name='leadorder_version')
    op.drop_index(op.f('ix_leadorder_version_end_transaction_id'), table_name='leadorder_version')
    op.drop_table('leadorder_version')

    # Creat leadorders table
    op.create_table(
        'leadorders_version',
        sa.Column('id', types.uuid.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_leadorders_version_end_transaction_id'),
        'leadorders_version', ['end_transaction_id'], unique=False
    )
    op.create_index(
        op.f('ix_leadorders_version_id'), 'leadorders_version', ['id'], unique=False)
    op.create_index(
        op.f('ix_leadorders_version_operation_type'),
        'leadorders_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_leadorders_version_transaction_id'),
        'leadorders_version', ['transaction_id'], unique=False)
    op.create_table('leadorders',
        sa.Column('id', types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leadorders_id'), 'leadorders', ['id'], unique=True)


def downgrade():
    """Downgrade database model."""
    op.create_table(
        'leadorders_version',
        sa.Column('id', types.uuid.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_leadorders_version_end_transaction_id'),
        'leadorders_version', ['end_transaction_id'], unique=False
    )
    op.create_index(
        op.f('ix_leadorders_version_id'), 'leadorders_version', ['id'], unique=False)
    op.create_index(
        op.f('ix_leadorders_version_operation_type'),
        'leadorders_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_leadorders_version_transaction_id'),
        'leadorders_version', ['transaction_id'], unique=False)
    op.create_table('leadorders',
        sa.Column('id', types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leadorders_id'), 'leadorders', ['id'], unique=True)
