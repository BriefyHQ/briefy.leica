"""Order reports."""
from briefy.leica.models import Order
from briefy.leica.reports import export_date_from_history
from briefy.leica.reports import export_datetime
from briefy.leica.reports import export_integer
from briefy.leica.reports import export_location
from briefy.leica.reports.base import BaseReport
from sqlalchemy.orm.query import Query


ORDER_CSV = '/tmp/orders.csv'


class AllOrders(BaseReport):
    """Report dumping all Orders."""

    fieldnames = (
        'customer_name',
        'project_name',
        'category',
        'input_date',
        'source',
        'uid',
        'briefy_id',
        'customer_order_id',
        'order_name',
        'street',
        'locality',
        'country',
        'number_required_assets',
        'scheduled_datetime',
        'submission_date',
        'submission_path',
        'order_status',
        'first_delivery_date',
        'last_deliver_date',
        'delivery_link',
        'last_refusal_date',
        'accept_date',
        'order_price_currency',
        'default_order_price',
        'delivery_sftp_link',
        'type',
        'actual_order_price',
    )

    @property
    def _query_(self) -> Query:
        """Return the query for this report.

        :return: Query object.
        """
        return Order.query().filter(Order.current_type == 'order')

    @staticmethod
    def transform(record: Order) -> dict:
        """Transform a record and result a record.

        :param record: Order to be transformed.
        :return: Dictionary with data already transformed.
        """
        state_history = record.state_history
        last_refusal_date = export_date_from_history(state_history, ('refuse',), first=False)
        accept_date = export_date_from_history(state_history, ('accept',), first=True)
        street, locality, country = export_location(record.location)
        asset_types = ','.join(record.asset_types)

        submission_date = None
        submission_path = None
        if record.assignments:
            assignment = record.assignments[-1]
            submission_date = assignment.submission_date
            submission_path = assignment.submission_path

        delivery_link = None
        delivery_sftp_link = None
        if record.delivery:
            if 'sftp' in record.delivery:
                delivery_sftp_link = record.delivery.get('sftp')

            if 'gdrive' in record.delivery:
                delivery_link = record.delivery.get('gdrive')
        payload = {
            'customer_name': record.customer.title,
            'project_name': record.project.title,
            'category': record.category.value,
            'input_date': export_datetime(record.created_at),
            'source': record.source.value,
            'uid': record.id,
            'briefy_id': record.slug,
            'customer_order_id': record.customer_order_id,
            'order_name': record.title,
            'street': street,
            'locality': locality,
            'country': country,
            'asset_type': asset_types,
            'number_required_assets': record.number_required_assets,
            'scheduled_datetime': export_datetime(record.scheduled_datetime),
            'submission_date': export_datetime(submission_date),
            'submission_path': submission_path,
            'order_status': record.state,
            'first_delivery_date': export_datetime(record.deliver_date),
            'last_deliver_date': export_datetime(record.last_deliver_date),
            'delivery_link': delivery_link,
            'last_refusal_date': export_datetime(last_refusal_date),
            'accept_date': export_datetime(accept_date),
            'order_price_currency': record.price_currency,
            'default_order_price': export_integer(record.price),
            'delivery_sftp_link': delivery_sftp_link,
            'type': record.type,
            'actual_order_price': export_integer(record.actual_order_price)
        }
        return payload


class ActiveOrders(AllOrders):
    """Report dumping orders for Active Projects."""

    fieldnames = (
        'customer_name',
        'project_name',
        'category',
        'uid',
        'briefy_id',
        'customer_order_id',
        'order_name',
        'locality',
        'country',
        'asset_type',
        'number_required_assets',
        'order_status',
        'first_delivery_date',
        'last_deliver_date',
        'last_refusal_date',
        'accept_date',
        'order_price_currency',
        'default_order_price',
        'actual_order_price'
    )

    @property
    def _query_(self) -> Query:
        """Return the query for this report.

        :return: Query object.
        """
        return Order.query().filter(
            Order.project.has(state='ongoing'),
            Order.current_type == 'order'
        )
