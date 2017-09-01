"""Fix assginment qa and scout manager localroles.

Revision ID: c8aa72b4d1c9
Revises: f63876ef69c6
Create Date: 2017-09-01 12:08:13.814076
"""
from alembic import op


revision = 'c8aa72b4d1c9'
down_revision = 'f63876ef69c6'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database model."""
    fix_assignments_localroles = '''
    UPDATE localroles SET role_name = source.role_name
    FROM
    (SELECT DISTINCT
    l.id,
    l.updated_at,
    u.title,
    CASE l.role_name
        WHEN 'assignment_internal_qa' THEN 'assignment_internal_scout'
        WHEN 'assignment_internal_scout' THEN 'assignment_internal_qa'
    END as role_name
    FROM localroles as l JOIN items as u on l.principal_id = u.id
    WHERE l.role_name IN ('assignment_internal_qa', 'assignment_internal_scout')
    AND l.updated_at <= '2017-09-01' ORDER BY l.updated_at DESC) as source
    WHERE source.id = localroles.id
    '''
    op.execute(fix_assignments_localroles)


def downgrade():
    """Downgrade database model."""
    pass
