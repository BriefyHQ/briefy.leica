"""Fix State History.

Revision ID: b94c5e4eabad
Revises: a7d84093cfcf
Create Date: 2017-08-02 17:18:44.791218
"""
from alembic import op


revision = 'b94c5e4eabad'
down_revision = 'a7d84093cfcf'
branch_labels = None
depends_on = None


UPDATES = '''
UPDATE
  items
SET
  state_history=history.state_history
FROM
(
  SELECT
    id,
    array_to_json(
      array_agg(
       jsonb_build_object(
        'from', src,
        'to', dest,
        'transition', transition,
        'date', created_at,
        'actor', actor,
        'message', message
       )
      )
    ) as state_history
  FROM
    (
    SELECT
       id,
       src,
       dest,
       case 
         when transition = '' then 'created'
         when transition != '' then transition  
       end as transition,
       created_at,
       case 
        when char_length(actor) = 36 then actor
        when char_length(actor) > 36 then (actor::jsonb)->> 'id'::text
        when actor is Null then 'be319e15-d256-4587-a871-c3476affa309'
        when actor = 'None' then 'be319e15-d256-4587-a871-c3476affa309'
       end as actor,
       message
    FROM
      (
         SELECT
          temp1.id,
          (temp1.transition ->> 'from'::text) AS src,
          (temp1.transition ->> 'to'::text) AS dest,
          (temp1.transition ->> 'transition'::text) AS transition,
          (temp1.transition ->> 'date'::text) AS created_at,
          (temp1.transition ->> 'actor'::text) AS actor,
          (temp1.transition ->> 'message'::text) AS message
         FROM (
            SELECT
              items.id,
              items.type,
              jsonb_array_elements(items.state_history) AS transition
            FROM items
            order by id
          ) temp1
      ) as temp2
    ) as cleansed_history
  GROUP BY 
    id
) as history
WHERE
  items.id = history.id
'''  # noQA


def data_upgrade():
    """Update data."""
    print(revision)
    # Update state history
    op.execute(UPDATES)


def upgrade():
    """Upgrade database model."""
    data_upgrade()


def downgrade():
    """Downgrade database model."""
    pass
