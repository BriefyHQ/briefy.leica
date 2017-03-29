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
        'field': 'total', 'label': 'All Orders',
        'type': 'integer', 'url': '', 'filter': ''
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
        'field': 'in_qa', 'label': 'Orders in QA process',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'cancelled', 'label': 'Cancelled Orders',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'completed', 'label': 'Completed Orders',
        'type': 'integer', 'url': '', 'filter': ''
    }
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
        'field': 'newly-delivered', 'label': 'Newly Delivered',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'further_revision', 'label': 'In Further Revision',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 're-delivered', 'label': 'Re-delivered',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'completed', 'label': 'Completed',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'rejected', 'label': 'Rejected',
        'type': 'integer', 'url': '', 'filter': ''
    },
    {
        'field': 'total', 'label': 'Total',
        'type': 'integer', 'url': '', 'filter': ''
    },
)
