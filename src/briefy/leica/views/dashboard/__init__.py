"""Dashboard models views."""

ORDER_PROJECT_COLS = (
    {
        'field': 'absolute_url', 'label': 'url',
        'type': 'hidden', 'url': '', 'filter': ''
    },
    {
        'field': 'title', 'label': 'Project',
        'type': 'text', 'url': 'absolute_url', 'filter': ''
    },
    {
        'field': 'received', 'label': 'New Orders',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'assigned', 'label': 'Assigned Orders',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'scheduled', 'label': 'Scheduled Orders',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'in_qa', 'label': 'In Briefy QA',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'cancelled', 'label': 'Cancelled Orders',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'delivered', 'label': 'Delivered Orders',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'total', 'label': 'Total',
        'type': 'integer', 'url': '', 'filter': ''
    },
)

DELIVERED_ORDERS_COLS = (
    {
        'field': 'absolute_url', 'label': 'url',
        'type': 'hidden', 'url': '', 'filter': ''
    },
    {
        'field': 'title', 'label': 'Project',
        'type': 'text', 'url': 'absolute_url', 'filter': ''
    },
    {
        'field': 'newly_delivered', 'label': 'Newly Delivered',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'further_revision', 'label': 'In Further Revision',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 're_delivered', 'label': 'Re-delivered',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'completed', 'label': 'Completed',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'total', 'label': 'Total',
        'type': 'integer', 'url': '', 'filter': ''
    },
)

LEAD_PROJECT_COLS = (
    {
        'field': 'absolute_url', 'label': 'url',
        'type': 'hidden', 'url': '', 'filter': ''
    },
    {
        'field': 'title', 'label': 'Project',
        'type': 'text', 'url': 'absolute_url', 'filter': ''
    },
    {
        'field': 'open', 'label': 'Open Leads',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'cancelled', 'label': 'Cancelled Leads',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'confirmed', 'label': 'Confirmed Leads',
        'type': 'integer', 'url': '', 'filter': ''
    },
)

DASHBOARD_ALL_ORDERS_CUSTOMER_QUERY = """
    SELECT
    count(active_orders.id) as total,
    active_orders.title,
    active_orders.project_id,

    sum(
    CASE WHEN
    active_orders.state = 'received'
    THEN 1 ELSE 0
    END) as received,

    sum(
    CASE WHEN
    active_orders.state = 'assigned'
    THEN 1 ELSE 0
    END) as assigned,

    sum(
    CASE WHEN
    active_orders.state = 'scheduled'
    THEN 1 ELSE 0
    END) as scheduled,

    sum(
    CASE WHEN
    active_orders.state = 'in_qa'
    AND active_orders.accept_date IS NULL
    THEN 1 ELSE 0
    END) as in_qa,

    sum(
    CASE WHEN active_orders.state = 'cancelled'
    THEN 1 ELSE 0
    END) as cancelled,

    sum(
    CASE WHEN
        active_orders.state = 'delivered'
        OR
        active_orders.state IN ('accepted', 'refused', 'perm_refused', 'in_qa')
        AND
        active_orders.accept_date IS NOT NULL
    THEN 1 ELSE 0
    END) as delivered

    FROM

    (SELECT DISTINCT orders.id, orders.project_id,
    projects.title, orders.state, orders.accept_date FROM

    (SELECT i.id, i.state, i.title, o.accept_date, o.project_id
    FROM items as i JOIN orders as o on i.id = o.id
    WHERE o.current_type = '{type}' AND
    i.state IN ('received', 'assigned', 'scheduled', 'cancelled',
    'delivered', 'accepted', 'in_qa', 'refused', 'perm_refused')
    ) as orders JOIN

    (SELECT i.id, i.state, i.title, p.customer_id, l.principal_id, l.role_name
    FROM items as i JOIN projects as p on i.id = p.id
    JOIN localroles as l on p.id = l.item_id) as projects
    on orders.project_id = projects.id JOIN

    (SELECT i.id, i.state, i.title, l.principal_id, l.role_name
    FROM items as i JOIN customers as c on i.id = c.id
    JOIN localroles as l on c.id = l.item_id) as customers
    on projects.customer_id = customers.id

    WHERE
    (customers.role_name IN ('customer_manager', 'internal_account')
    AND customers.principal_id = '{principal_id}')
    OR projects.principal_id = '{principal_id}'

    ) as active_orders GROUP BY
    active_orders.title,
    active_orders.project_id
    ORDER BY active_orders.title
    """
