"""Order reports."""
from briefy.common.utilities.interfaces import IUserProfileQuery
from briefy.leica.models import Assignment
from briefy.leica.reports import export_date_from_history
from briefy.leica.reports import export_datetime
from briefy.leica.reports import export_location
from briefy.leica.reports import export_money_to_fixed_point
from briefy.leica.reports.base import BaseReport
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.query import Query
from zope.component import getUtility


ASSIGNMENT_CSV = '/tmp/assignments.csv'


class AllAssignments(BaseReport):
    """Report dumping all Assignments."""

    fieldnames = (
        'project_name',
        'category',
        'uid',
        'briefy_id',
        'customer_order_id',
        'assignment_name',
        'locality',
        'country',
        'number_required_assets',
        'responsible_professional',
        'assignment_status',
        'set_type',
        'scheduled_datetime',
        'first_submission_date',
        'last_submission_date',
        'submission_path',
        'last_approval_date',
        'last_refusal_date',
        'complete_date',
        'assignment_price_currency',
        'actual_assignment_price',
        'actual_assignment_travel_expenses',
        'actual_assignment_additional_compensation',
        'reason_additional_compensation',
    )

    @property
    def _query_(self) -> Query:
        """Return the query for this report.

        :return: Query object.
        """
        return Assignment.query().options(
            joinedload('order').joinedload('project')
        )

    @staticmethod
    def transform(record: Assignment) -> dict:
        """Transform a record and result a record.

        :param record: Assignment to be transformed.
        :return: Dictionary with data already transformed.
        """
        project = record.order.project
        history = record.state_history
        street, locality, country = export_location(record.location)
        last_approval_date = export_date_from_history(history, ('approve',), first=False)
        last_refusal_date = export_date_from_history(history, ('refuse',), first=False)
        complete_date = export_date_from_history(history, ('complete',), first=True)
        asset_types = ','.join(record.asset_types)

        payload = {
            'project_name': project.title,
            'uid': record.id,
            'briefy_id': record.slug,
            'customer_order_id': record.customer_order_id,
            'assignment_name': record.title,
            'locality': locality,
            'country': country,
            'asset_type': asset_types,
            'number_required_assets': record.number_required_assets,
            'responsible_professional': record.professional.title if record.professional else None,
            'assignment_status': record.state,
            'set_type': record.set_type.value if record.set_type else None,
            'scheduled_datetime': export_datetime(record.scheduled_datetime),
            'first_submission_date': export_datetime(record.submission_date),
            'last_submission_date': export_datetime(record.last_submission_date),
            'submission_path': record.submission_path,
            'last_approval_date': export_datetime(last_approval_date),
            'last_refusal_date': export_datetime(last_refusal_date),
            'complete_date': export_datetime(complete_date),
            'assignment_price_currency': record.payout_currency,
            'actual_assignment_price': export_money_to_fixed_point(record.payout_value),
            'actual_assignment_travel_expenses': export_money_to_fixed_point(
                record.travel_expenses
            ),
            'actual_assignment_additional_compensation': export_money_to_fixed_point(
                record.additional_compensation
            ),
            'reason_additional_compensation': record.reason_additional_compensation
        }
        return payload


class ActiveAssignments(AllAssignments):
    """Report dumping Assignments for active projects."""

    fieldnames = (
        'project_name',
        'category',
        'uid',
        'briefy_id',
        'assignment_name',
        'locality',
        'country',
        'asset_type',
        'number_required_assets',
        'responsible_professional',
        'assignment_status',
        'set_type',
        'first_submission_date',
        'last_submission_date',
        'last_approval_date',
        'complete_date',
        'assignment_price_currency',
        'actual_assignment_price',
        'actual_assignment_travel_expenses',
        'actual_assignment_additional_compensation',
        'reason_additional_compensation'
    )

    @property
    def _query_(self) -> Query:
        """Return the query for this report.

        :return: Query object.
        """
        return Assignment.query().filter(
            Assignment.project.has(state='ongoing'),
            Assignment.order.has(current_type='order'),
        ).options(
            joinedload('order').joinedload('project')
        )


class AssignmentsQAFollowUP(ActiveAssignments):
    """Report QA Assignments for active projects."""

    fieldnames = (
        'customer_name',
        'project_name',
        'briefy_assignment_id',
        'customer_order_id',
        'assignment_status',
        'responsible_qa_manager',
        'first_submission_date',
        'last_submission_date',
        'first_rejection_date',
        'last_rejection_date',
        'first_approval_date',
        'last_approval_date',
        'first_refusal_date',
        'last_refusal_date',
    )

    @property
    def _query_(self) -> Query:
        """Return the query for this report.

        :return: Query object.
        """
        return Assignment.query().filter(
            Assignment.project.has(state='ongoing'),
            Assignment.order.has(current_type='order'),
        ).options(
            joinedload('order').joinedload('project').joinedload('customer')
        )

    @staticmethod
    def transform(record: Assignment) -> dict:
        """Transform a record and result a record.

        :param record: Assignment to be transformed.
        :return: Dictionary with data already transformed.
        """
        profile_service = getUtility(IUserProfileQuery)

        p = ActiveAssignments.transform(record)
        history = record.state_history
        customer = record.project.customer
        p['customer_name'] = customer.title
        p['briefy_assignment_id'] = p['briefy_id']
        p['responsible_qa_manager'] = ''
        if record.qa_manager:
            data = profile_service.get_data(str(record.qa_manager))
            p['responsible_qa_manager'] = data['fullname']
        p['first_rejection_date'] = export_date_from_history(history, ('reject',), first=True)
        p['last_rejection_date'] = export_date_from_history(history, ('reject',), first=False)
        p['first_approval_date'] = export_date_from_history(history, ('approve',), first=True)
        p['first_refusal_date'] = export_date_from_history(history, ('refuse',), first=True)

        return p
