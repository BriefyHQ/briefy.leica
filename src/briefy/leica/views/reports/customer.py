"""Views to handle Customer Dashboards."""
from briefy.leica.models.reports.customer import OrdersByProjectReport
from briefy.leica.views.reports import BaseReport
from briefy.ws import CORS_POLICY
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow

STATES = {
    'created': 'Created',
    'received': 'New',
    'assigned': 'Assigned',
    'scheduled': 'Scheduled',
    'cancelled': 'Cancelled',
    'in_qa': 'In QA Process',
    'delivered': 'Delivered',
    'accepted': 'Completed',
    'refused': 'In Further Revision',
    'perm_refused': 'Rejected'
}


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

    def convert_data(self, data: OrdersByProjectReport):
        """Apply some basic type conversions."""
        created_at = data.created_at
        scheduled_datetime = data.scheduled_datetime
        deliver_date = data.deliver_date
        timezone = data.timezone
        response = {
            'Briefy ID': data.briefy_id,
            'Order ID': data.customer_order_id,
            'Order Name': data.title,
            'Project Name': data.project_title,
            'Status': STATES.get(data.state, data.state),
            'Input Date': self._format_datetime(created_at, timezone, False),
            'Shooting Date': self._format_datetime(scheduled_datetime, timezone, True),
            'Delivery Date': self._format_datetime(deliver_date, timezone, False),
        }
        return response

    def default_filters(self, query) -> object:
        """Default filters to be applied to every query.

        This is supposed to be specialized by resource classes.
        :returns: A tuple of default filters to be applied to queries.
        """
        user = self.request.user
        project_id = self.request.matchdict.get('id', '')
        query = query.params(
            user_id_1=user.id,
            project_id_1=project_id,
        )
        return query
