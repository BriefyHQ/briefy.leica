"""New LeadOrder type..

Revision ID: bccb04f1f444
Revises: 53ae41d53636
Create Date: 2017-05-03 12:00:41.829473
"""
from alembic import op
from briefy.leica.vocabularies import OrderTypeChoices
from sqlalchemy_utils import types


import sqlalchemy as sa


revision = 'bccb04f1f444'
down_revision = '53ae41d53636'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.create_table(
        'leadorder_version',
        sa.Column('id', types.uuid.UUIDType(), autoincrement=False, nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_leadorder_version_end_transaction_id'),
        'leadorder_version', ['end_transaction_id'], unique=False
    )
    op.create_index(
        op.f('ix_leadorder_version_id'), 'leadorder_version', ['id'], unique=False)
    op.create_index(
        op.f('ix_leadorder_version_operation_type'),
        'leadorder_version', ['operation_type'], unique=False)
    op.create_index(
        op.f('ix_leadorder_version_transaction_id'),
        'leadorder_version', ['transaction_id'], unique=False)
    op.create_table('leadorder',
        sa.Column('id', types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leadorder_id'), 'leadorder', ['id'], unique=True)
    op.add_column('orders', sa.Column('type', sa.String(), nullable=True))
    op.add_column(
        'orders_version', sa.Column('type', sa.String(), autoincrement=False, nullable=True)
    )
    op.add_column(
        'projects',
        sa.Column(
            'order_type',
            types.choice.ChoiceType(OrderTypeChoices,  impl=sa.String()),
            server_default='order',
            nullable=False
        )
    )
    op.add_column(
        'projects_version',
        sa.Column(
            'order_type',
            types.choice.ChoiceType(OrderTypeChoices,  impl=sa.String()),
            server_default='order',
            autoincrement=False,
            nullable=True
        )
    )


def downgrade():
    """Downgrade database model."""
    op.drop_column('projects_version', 'order_type')
    op.drop_column('projects', 'order_type')
    op.drop_column('orders_version', 'type')
    op.drop_column('orders', 'type')
    op.drop_index(op.f('ix_leadorder_id'), table_name='leadorder')
    op.drop_table('leadorder')
    op.drop_index(op.f('ix_leadorder_version_transaction_id'), table_name='leadorder_version')
    op.drop_index(op.f('ix_leadorder_version_operation_type'), table_name='leadorder_version')
    op.drop_index(op.f('ix_leadorder_version_id'), table_name='leadorder_version')
    op.drop_index(op.f('ix_leadorder_version_end_transaction_id'), table_name='leadorder_version')
    op.drop_table('leadorder_version')
