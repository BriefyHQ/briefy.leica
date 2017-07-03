"""Views to handle internal Reports."""
from briefy.leica.reports.assignments import ActiveAssignments
from briefy.leica.reports.assignments import AllAssignments
from briefy.leica.reports.assignments import AssignmentsQAFollowUP
from briefy.leica.reports.customers import AllCustomers
from briefy.leica.reports.orders import ActiveOrders
from briefy.leica.reports.orders import AllOrders
from briefy.leica.reports.professionals import AllProfessionals
from briefy.leica.views.reports import BaseReport
from briefy.ws import CORS_POLICY
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow
from pyramid.security import Everyone


ASSIGNMENT_REPORTS = {
    'all': AllAssignments,
    'active': ActiveAssignments,
    'qa': AssignmentsQAFollowUP
}


CUSTOMER_REPORTS = {
    'all': AllCustomers
}


ORDER_REPORTS = {
    'all': AllOrders,
    'active': ActiveOrders,
}

PROFESSIONAL_REPORTS = {
    'all': AllProfessionals
}


class InternalReportFactory(BaseFactory):
    """Internal report context factory."""

    __base_acl__ = [
        (Allow, Everyone, ['list', 'view']),
    ]


class MsOphelieReport(BaseReport):
    """Report generation for Ms. Ophelie."""

    reports = None

    def get_report_data(self, filename: str):
        """Execute the report, return a tuple with data and metadata."""
        report_id = self.request.matchdict.get('id', '')
        all_reports = self.reports
        if not (all_reports and report_id in all_reports):
            raise HTTPNotFound('Report not found')
        content_type = self.mime_type
        report = all_reports[report_id]()
        csv_file = report()
        data = csv_file.getvalue()
        return filename, content_type, data


@resource(
    path='/ms-ophelie/assignments/{id}',
    cors_policy=CORS_POLICY,
    factory=InternalReportFactory
)
class MsOphelieAssignments(MsOphelieReport):
    """Assignment report for Ms. Ophelie."""

    filename = 'assignments.csv'
    reports = ASSIGNMENT_REPORTS


@resource(
    path='/ms-ophelie/customers/{id}',
    cors_policy=CORS_POLICY,
    factory=InternalReportFactory
)
class MsOphelieCustomers(MsOphelieReport):
    """Customer report for Ms. Ophelie."""

    filename = 'customers.csv'
    reports = CUSTOMER_REPORTS


@resource(
    path='/ms-ophelie/orders/{id}',
    cors_policy=CORS_POLICY,
    factory=InternalReportFactory
)
class MsOphelieOrders(MsOphelieReport):
    """Order report for Ms. Ophelie."""

    filename = 'orders.csv'
    reports = ORDER_REPORTS


@resource(
    path='/ms-ophelie/professionals/{id}',
    cors_policy=CORS_POLICY,
    factory=InternalReportFactory
)
class MsOphelieProfessionals(MsOphelieReport):
    """Customer report for Ms. Ophelie."""

    filename = 'professionals.csv'
    reports = PROFESSIONAL_REPORTS
