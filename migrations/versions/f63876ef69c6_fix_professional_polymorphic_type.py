"""Fix professional polymorphic type.

Revision ID: f63876ef69c6
Revises: 3cdbc7e26519
Create Date: 2017-08-16 15:44:51.923763
"""
from alembic import op


revision = 'f63876ef69c6'
down_revision = '3cdbc7e26519'
branch_labels = None
depends_on = None

INSERT_TO_PHOTOGRAPHERS = """
INSERT INTO photographers 
  (id)
select id from items where type='professional';
"""  # noQA

CHANGE_TYPE = """
UPDATE items set type='photographer' where type in ('professional', 'photographers');
"""  # noQA


def data_upgrade():
    """Update data."""
    print(revision)
    # Add Professionals to Photographers
    op.execute(INSERT_TO_PHOTOGRAPHERS)
    # Change polymorphic type to photographer
    op.execute(CHANGE_TYPE)


def upgrade():
    """Upgrade database model."""
    data_upgrade()


def downgrade():
    """Downgrade database model."""
    pass
