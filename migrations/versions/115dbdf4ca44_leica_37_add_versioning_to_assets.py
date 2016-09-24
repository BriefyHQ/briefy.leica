"""LEICA-37-Add versioning to assets

Revision ID: 115dbdf4ca44
Revises: fd5b6154286b
Create Date: 2016-09-23 19:02:05.390933
"""
from alembic import op


import briefy.common
import sqlalchemy as sa
import sqlalchemy_utils

revision = '115dbdf4ca44'
down_revision = 'fd5b6154286b'
branch_labels = None
depends_on = None


# Monkey patch calls for which alembic create bogus parameters:

original_uuid_type = sqlalchemy_utils.types.uuid.UUIDType


def monkey_uuid_type(*args, length=None, **kw):
    return original_uuid_type(*args, **kw)

sqlalchemy_utils.types.uuid.UUIDType = monkey_uuid_type

original_timezone_type = sqlalchemy_utils.types.timezone.TimezoneType


def monkey_timezone_type(*args, length=None, **kw):
    return original_timezone_type(*args, **kw)

sqlalchemy_utils.types.timezone.TimezoneType = monkey_timezone_type


def upgrade():
    """Upgrade database model."""
    op.drop_column('assets', 'version')
    op.create_table(
        'assets_version',
        sa.Column(
            'id', sqlalchemy_utils.types.uuid.UUIDType(length=16),
            autoincrement=False, nullable=False
        ),
        sa.Column('source_path', sa.String(length=1000), autoincrement=False, nullable=True),
        sa.Column('filename', sa.String(length=1000), autoincrement=False, nullable=True),
        sa.Column('content_type', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('size', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('width', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column('height', sa.Integer(), autoincrement=False, nullable=True),
        sa.Column(
            'raw_metadata',
            sqlalchemy_utils.types.json.JSONType(), autoincrement=False, nullable=True
        ),
        sa.Column(
            'created_at', briefy.common.db.types.aware_datetime.AwareDateTime(),
            autoincrement=False, nullable=True
        ),
        sa.Column(
            'updated_at', briefy.common.db.types.aware_datetime.AwareDateTime(),
            autoincrement=False, nullable=True
        ),
        sa.Column('state', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('title', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
        sa.Column('owner', sa.String(length=255), autoincrement=False, nullable=True),
        sa.Column(
            'author_id', sqlalchemy_utils.types.uuid.UUIDType(length=16),
            autoincrement=False, nullable=True
        ),
        sa.Column(
            'uploaded_by', sqlalchemy_utils.types.uuid.UUIDType(length=16),
            autoincrement=False, nullable=True
        ),
        sa.Column(
            'job_id', sqlalchemy_utils.types.uuid.UUIDType(length=16),
            autoincrement=False, nullable=True
        ),
        sa.Column(
            'history',
            sqlalchemy_utils.types.json.JSONType(), autoincrement=False, nullable=True
        ),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(
        op.f('ix_assets_version_end_transaction_id'),
        'assets_version', ['end_transaction_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_assets_version_operation_type'),
        'assets_version', ['operation_type'],
        unique=False
    )
    op.create_index(
        op.f('ix_assets_version_transaction_id'),
        'assets_version',
        ['transaction_id'],
        unique=False
    )
    op.create_table(
        'transaction',
        sa.Column('issued_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('remote_addr', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    """Downgrade database model."""
    op.drop_table('transaction')
    op.drop_index(
        op.f('ix_assets_version_transaction_id'), table_name='assets_version'
    )
    op.drop_index(
        op.f('ix_assets_version_operation_type'), table_name='assets_version'
    )
    op.drop_index(
        op.f('ix_assets_version_end_transaction_id'), table_name='assets_version'
    )
    op.add_column(
        'assets',
        sa.Column('version', sa.Integer(), nullable=False),
    )
    op.drop_table('assets_version')
