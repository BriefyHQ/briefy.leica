"""Create report views.

Revision ID: 3cdbc7e26519
Revises: b94c5e4eabad
Create Date: 2017-08-07 14:10:03.060092
"""
from alembic import op


revision = '3cdbc7e26519'
down_revision = 'b94c5e4eabad'
branch_labels = None
depends_on = None


EVENT_HISTORY_VIEW = """
DROP VIEW IF EXISTS events_history;
CREATE VIEW events_history AS
SELECT
    temp1.id,
    temp1.type,
    concat(temp1.type, '.workflow.', (temp1.transition ->> 'transition'::text))::text as event_name,
    (temp1.transition ->> 'from'::text) AS src,
    (temp1.transition ->> 'to'::text) AS dest,
    (temp1.transition ->> 'transition'::text) AS transition,
    (temp1.transition ->> 'date'::text)::timestamp AS date,
    (temp1.transition ->> 'actor'::text) AS actor,
    (temp1.transition ->> 'message'::text) AS message
FROM (
  SELECT 
     items.id,
     items.type,
     jsonb_array_elements(items.state_history) AS transition
  FROM
     items
  ) temp1
ORDER BY 
  temp1.id,
  (temp1.transition ->> 'date'::text)::timestamp;
"""  # noQA


ASSIGNMENTS_HISTORY_VIEW = """
    DROP VIEW IF EXISTS assignments_history;
    CREATE VIEW assignments_history as
    select
        id,
        type,
        event_name,
        src,
        dest,
        transition,
        date,
        actor,
        message
    from
        events_history
    where
        type in ('assignment');
"""


ASSIGNMENTS_REPORTS_VIEWS = """
    DROP VIEW IF EXISTS assignments_history_last_day;
    CREATE VIEW assignments_history_last_day as
    select
       event_name,
       count(distinct(id)) as total
    from assignments_history
    where
      to_char(date, 'YYYY-MM-DD') = to_char(current_date - 1, 'YYYY-MM-DD')
    group by
      event_name;

    DROP VIEW IF EXISTS assignments_history_last_month;
    CREATE VIEW assignments_history_last_month as
    select
       event_name,
       count(distinct(id)) as total
    from assignments_history
    where
      to_char(date, 'YYYY-MM') = to_char(current_date - interval '1' month, 'YYYY-MM')
    group by
      event_name;
"""


ORDERS_HISTORY_VIEW = """
    DROP VIEW IF EXISTS orders_history;
    CREATE VIEW orders_history as
    select
        id,
        type,
        concat('order', '.workflow.', transition)::text as event_name,
        src,
        dest,
        transition,
        date,
        actor,
        message
    from
        events_history
    where
        type in ('order', 'leadorder');
"""


ORDERS_REPORTS_VIEWS = """
    DROP VIEW IF EXISTS orders_history_last_day;
    CREATE VIEW orders_history_last_day as
    select
       event_name,
       count(distinct(id)) as total
    from orders_history
    where
      to_char(date, 'YYYY-MM-DD') = to_char(current_date - 1, 'YYYY-MM-DD')
    group by
      event_name;

    DROP VIEW IF EXISTS orders_history_last_month;
    CREATE VIEW orders_history_last_month as
    select
       event_name,
       count(distinct(id)) as total
    from orders_history
    where
      to_char(date, 'YYYY-MM') = to_char(current_date - interval '1' month, 'YYYY-MM')
    group by
      event_name;
"""


def history_view():
    """Create order reports views."""
    op.execute(EVENT_HISTORY_VIEW)


def assignment_views():
    """Create order reports views."""
    op.execute(ORDERS_HISTORY_VIEW)
    op.execute(ORDERS_REPORTS_VIEWS)


def order_views():
    """Create order reports views."""
    op.execute(ASSIGNMENTS_HISTORY_VIEW)
    op.execute(ASSIGNMENTS_REPORTS_VIEWS)


def upgrade():
    """Upgrade database model."""
    print(revision)
    print('Event History view')
    history_view()
    print('Assignment History and reports views')
    assignment_views()
    print('Order History and reports views')
    order_views()


def downgrade():
    """Downgrade database model."""
    op.execute('DROP VIEW IF EXISTS assignments_history_last_day;')
    op.execute('DROP VIEW IF EXISTS assignments_history_last_month;')
    op.execute('DROP VIEW IF EXISTS assignments_history;')
    op.execute('DROP VIEW IF EXISTS orders_history_last_day;')
    op.execute('DROP VIEW IF EXISTS orders_history_last_month;')
    op.execute('DROP VIEW IF EXISTS orders_history;')
    op.execute('DROP VIEW IF EXISTS events_history;')
