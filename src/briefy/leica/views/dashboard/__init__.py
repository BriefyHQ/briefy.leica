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
