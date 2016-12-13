"""Job Assignment.

Revision ID: 488db43730a4
Revises: 23b321174b18
Create Date: 2016-12-05 13:06:54.557369
"""
from alembic import op
from briefy.common.db.types.aware_datetime import AwareDateTime
from sqlalchemy_utils.types.uuid import UUIDType

import sqlalchemy as sa
import sqlalchemy_utils

revision = '488db43730a4'
down_revision = '23b321174b18'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    op.create_table('jobassignments_version',
                    sa.Column('id', UUIDType(), autoincrement=False, nullable=False),
                    sa.Column('created_at', AwareDateTime(),
                              autoincrement=False, nullable=True),
                    sa.Column('updated_at', AwareDateTime(),
                              autoincrement=False, nullable=True),
                    sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('payout_currency',
                              sqlalchemy_utils.types.currency.CurrencyType(length=3),
                              autoincrement=False, nullable=True),
                    sa.Column('payout_value', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('travel_expenses', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('additional_compensation', sa.Integer(), autoincrement=False,
                              nullable=True),
                    sa.Column('payable', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('job_id', UUIDType(), autoincrement=False, nullable=True),
                    sa.Column('professional_id', UUIDType(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False,
                              nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('id', 'transaction_id')
                    )
    op.create_index(op.f('ix_jobassignments_version_end_transaction_id'), 'jobassignments_version',
                    ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_jobassignments_version_operation_type'), 'jobassignments_version',
                    ['operation_type'], unique=False)
    op.create_index(op.f('ix_jobassignments_version_transaction_id'), 'jobassignments_version',
                    ['transaction_id'], unique=False)
    op.create_table('jobassignments',
                    sa.Column('id', UUIDType(), nullable=False),
                    sa.Column('created_at', AwareDateTime(),
                              nullable=True),
                    sa.Column('updated_at', AwareDateTime(),
                              nullable=True),
                    sa.Column('state', sa.String(length=100), nullable=True),
                    sa.Column('state_history', sqlalchemy_utils.types.json.JSONType(),
                              nullable=True),
                    sa.Column('payout_currency',
                              sqlalchemy_utils.types.currency.CurrencyType(length=3),
                              nullable=True),
                    sa.Column('payout_value', sa.Integer(), nullable=False),
                    sa.Column('travel_expenses', sa.Integer(), nullable=False),
                    sa.Column('additional_compensation', sa.Integer(), nullable=False),
                    sa.Column('payable', sa.Boolean(), nullable=False),
                    sa.Column('job_id', UUIDType(), nullable=False),
                    sa.Column('professional_id', UUIDType(), nullable=False),
                    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
                    sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_unique_constraint(None, 'customerbillingaddresses', ['id'])
    op.create_unique_constraint(None, 'customercontacts', ['id'])


def downgrade():
    """Downgrade database model."""
    op.drop_constraint(None, 'customercontacts', type_='unique')
    op.drop_constraint(None, 'customerbillingaddresses', type_='unique')
    op.drop_table('jobassignments')
    op.drop_index(op.f('ix_jobassignments_version_transaction_id'),
                  table_name='jobassignments_version')
    op.drop_index(op.f('ix_jobassignments_version_operation_type'),
                  table_name='jobassignments_version')
    op.drop_index(op.f('ix_jobassignments_version_end_transaction_id'),
                  table_name='jobassignments_version')
    op.drop_table('jobassignments_version')
