"""Views to handle Customer Dashboards."""
from briefy.leica.models.reports.customer import OrdersByProjectReport
from briefy.leica.views.reports import BaseReport
from briefy.ws import CORS_POLICY
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from datetime import datetime
from pyramid.security import Allow
from pytz import timezone

import typing as t


STATES = {
    'created': 'Created',
    'received': 'New',
    'assigned': 'Assigned',
    'scheduled': 'Scheduled',
    'cancelled': 'Cancelled',
    'in_qa': 'In Briefy QA',
    'delivered': 'Delivered',
    'accepted': 'Completed',
    'refused': 'In Further Revision',
    'perm_refused': 'Rejected'
}


def get_label_for_order_status(raw_state: str, accept_date: datetime) -> str:
    """Return the label for the Order state."""
    state = STATES.get(raw_state, raw_state)
    if raw_state == 'in_qa' and accept_date:
        state = 'In Further Revision'
    elif raw_state == 'delivered' and accept_date:
        state = 'Re-delivered'
    return state


class ReportCustomerFactory(BaseFactory):
    """Report Customer context factory."""

    model = OrdersByProjectReport

    __base_acl__ = [
        (Allow, 'g:customers', ['list', 'view']),
    ]


@resource(
    path='/reports/customer/projects/{id}',
    cors_policy=CORS_POLICY,
    factory=ReportCustomerFactory
)
class CustomerReports(BaseReport):
    """Reports for Customer."""

    model = OrdersByProjectReport
    filename = 'orders.csv'
    column_order = (
        'Briefy ID',
        'Order ID',
        'Order Name',
        'Project Name',
        'Status',
        'Input Date',
        'Shooting Date',
        'Delivery Date',
    )

    def convert_data(self, data: tuple):
        """Apply some basic type conversions."""
        slug, customer_order_id, title, project_title, \
            state, created_at, scheduled_datetime, deliver_date, \
            accept_date, timezone_str = data

        timezone_obj = timezone(timezone_str)
        response = {
            'Briefy ID': slug,
            'Order ID': customer_order_id,
            'Order Name': title,
            'Project Name': project_title,
            'Status': get_label_for_order_status(state, accept_date),
            'Input Date': self._format_datetime(created_at, timezone_obj, False),
            'Shooting Date': self._format_datetime(scheduled_datetime, timezone_obj, True),
            'Delivery Date': self._format_datetime(deliver_date, timezone_obj, False),
        }
        return response

    def results(self) -> t.Iterator:
        """Return the results iterator."""
        session = self.request.db
        raw_query = """
        SELECT DISTINCT
        orders.slug,
        orders.customer_order_id,
        orders.title,
        projects.title,
        orders.state,
        orders.created_at,
        orders.scheduled_datetime,
        orders.deliver_date,
        orders.accept_date,
        orders.timezone

        FROM

        (SELECT i.slug, i.state, i.title, o.accept_date, o.project_id,
        o.customer_order_id, i.created_at, o.scheduled_datetime,
        o.deliver_date, o.timezone
        FROM items as i JOIN orders as o on i.id = o.id
        ) as orders JOIN

        (SELECT i.id, i.state, i.title, p.customer_id, l.principal_id, l.role_name
        FROM items as i JOIN projects as p on i.id = p.id
        JOIN localroles as l on p.id = l.item_id
        WHERE l.principal_id = '{principal_id}') as projects
        on orders.project_id = projects.id

        WHERE projects.id = '{project_id}'
        ORDER BY orders.created_at
        """
        user = self.request.user
        project_id = self.request.matchdict.get('id', '')
        query = raw_query.format(principal_id=user.id, project_id=project_id)
        return session.execute(query)
