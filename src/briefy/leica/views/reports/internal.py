"""Views to handle internal Reports."""
from briefy.leica.tools.finance_csv_export import export_assignment
from briefy.leica.tools.finance_csv_export import export_order
from briefy.leica.views.reports import BaseReport
from briefy.ws import CORS_POLICY
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow
from pyramid.security import Everyone

import newrelic.agent


class InternalReportFactory(BaseFactory):
    """Internal report context factory."""

    __base_acl__ = [
        (Allow, Everyone, ['list', 'view']),
    ]


@resource(
    path='/ms-ophelie/assignments',
    cors_policy=CORS_POLICY,
    factory=InternalReportFactory
)
class MsOphelieAssignments(BaseReport):
    """Assignment report for Ms. Ophelie."""

    filename = 'assignments.csv'

    def get_report_data(self, filename: str):
        """Execute the report, return a tuple with data and metadata."""
        content_type = self.mime_type
        application = newrelic.agent.application()
        with newrelic.agent.BackgroundTask(application, name=filename, group='Reports'):
            csv_file = export_assignment()
            data = csv_file.getvalue()
            return filename, content_type, data


@resource(
    path='/ms-ophelie/orders',
    cors_policy=CORS_POLICY,
    factory=InternalReportFactory
)
class MsOphelieOrders(BaseReport):
    """Order report for Ms. Ophelie."""

    filename = 'orders.csv'

    def get_report_data(self, filename: str):
        """Execute the report, return a tuple with data and metadata."""
        content_type = self.mime_type
        application = newrelic.agent.application()
        with newrelic.agent.BackgroundTask(application, name=filename, group='Reports'):
            csv_file = export_order()
            data = csv_file.getvalue()
            return filename, content_type, data
