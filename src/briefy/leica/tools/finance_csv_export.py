"""Export all data for finance invoice."""
from briefy.leica.db import Session
from briefy.leica.models import Assignment
from briefy.leica.models import Order
from briefy.leica.sync import db
from briefy.leica.utils.transitions import get_transition_date_from_history
from datetime import datetime
from decimal import Decimal

import csv

ORDER_CSV = '/tmp/orders.csv'
ASSIGNMENT_CSV = '/tmp/assignments.csv'

DATETIME_EXPORT = '%Y-%m-%d %H:%M:%S'
DATETIME_TRANSFORM01 = '%Y-%m-%dT%H:%M:%S'
DATETIME_TRANSFORM02 = '%Y-%m-%dT%H:%M:%S.%f'


def convert_json_datetime(
        item: object,
        transitions: tuple = (),
        first: bool = False
) -> datetime:
    """Convert workflow dates in str format to datetime."""
    state_history = item.state_history
    date = get_transition_date_from_history(
        transitions, state_history, first=first,
    )
    try:
        date = datetime.strptime(date[:-6], DATETIME_TRANSFORM01) if date else None
    except ValueError:
        date = datetime.strptime(date[:-6], DATETIME_TRANSFORM02) if date else None

    return date


def export_datetime(date: datetime) -> str:
    """Format datetime to csv export."""
    return date.strftime(DATETIME_EXPORT) if date else None


def export_integer(value: int) -> Decimal:
    """Convert integer to decimal."""
    return Decimal(value) / Decimal(100) if value else None


def export_location(location: object) -> tuple:
    """Extract location data from location object."""
    if location:
        street = location.info.get('route')
        locality = location.locality
        country = location.country.code
    else:
        street = ''
        locality = ''
        country = ''

    return street, locality, country


def export_order():
    """Export all orders to csv file."""
    all_orders = Order.query().all()
    results = []
    for item in all_orders:
        last_refusal_date = convert_json_datetime(item, ('refuse',), first=False)
        accept_date = convert_json_datetime(item, ('accept',), first=True)
        street, locality, country = export_location(item.location)

        if item.assignments:
            assignment = item.assignments[-1]
            submission_date = assignment.submission_date
            submission_path = assignment.submission_path
        else:
            submission_date = None
            submission_path = None

        if item.delivery and 'sftp' in item.delivery:
            delivery_link = item.delivery.get('sftp')
        elif item.delivery and 'gdrive' in item.delivery:
            delivery_link = item.delivery.get('gdrive')
        else:
            delivery_link = None

        payload = dict(
            project_name=item.project.title,
            category=item.category.value,
            input_date=export_datetime(item.created_at),
            source=item.source.value,
            uid=item.id,
            briefy_id=item.slug,
            customer_order_id=item.customer_order_id,
            order_name=item.title,
            street=street,
            locality=locality,
            country=country,
            number_required_assets=item.number_required_assets,
            scheduled_datetime=export_datetime(item.scheduled_datetime),
            submission_date=export_datetime(submission_date),
            submission_path=submission_path,
            order_status=item.state,
            first_delivery_date=export_datetime(item.deliver_date),
            last_deliver_date=export_datetime(item.last_deliver_date),
            delivery_link=delivery_link,
            last_refusal_date=export_datetime(last_refusal_date),
            accept_date=export_datetime(accept_date),
            price_currency=item.price_currency,
            price=export_integer(item.price)
        )
        results.append(payload)
        print('Order appended: {id}'.format(id=item.id))
    file_out = open(ORDER_CSV, 'w')
    fieldnames = [
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
        'price_currency',
        'price'
    ]
    writer = csv.DictWriter(file_out, fieldnames=fieldnames)
    writer.writeheader()
    for data in results:
        writer.writerow(data)
    file_out.close()


def export_assignment():
    """Export all assignment to csv file."""
    all_assignments = Assignment.query().all()
    results = []
    file_out = open(ASSIGNMENT_CSV, 'w')
    for item in all_assignments:
        street, locality, country = export_location(item.location)
        last_approval_date = convert_json_datetime(item, ('approve',), first=False)
        last_refusal_date = convert_json_datetime(item, ('refuse',), first=False)
        complete_date = convert_json_datetime(item, ('complete',), first=True)

        payload = dict(
            project_name=item.order.project.title,
            category=item.order.category.value,
            uid=item.id,
            briefy_id=item.slug,
            customer_order_id=item.customer_order_id,
            assignment_name=item.title,
            locality=locality,
            country=country,
            number_required_assets=item.number_required_assets,
            responsible_professional=item.professional.title if item.professional else None,
            assignment_status=item.state,
            set_type=item.set_type.value if item.set_type else None,
            scheduled_datetime=export_datetime(item.scheduled_datetime),
            last_submission_date=export_datetime(item.last_submission_date),
            submission_path=item.submission_path,
            last_approval_date=last_approval_date,
            last_refusal_date=last_refusal_date,
            accept_date=complete_date,
            payout_currency=item.payout_currency,
            payout_value=export_integer(item.payout_value),
            travel_expenses=export_integer(item.travel_expenses),
            additional_compensation=export_integer(item.additional_compensation),
            reason_additional_compensation=item.reason_additional_compensation
        )
        results.append(payload)
        print('Assignment appended: {id}'.format(id=item.id))

    fieldnames = [
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
        'last_submission_date',
        'submission_path',
        'last_approval_date',
        'last_refusal_date',
        'complete_date',
        'payout_currency',
        'payout_value',
        'travel_expenses',
        'additional_compensation',
        'reason_additional_compensation',
    ]
    writer = csv.DictWriter(file_out, fieldnames=fieldnames)
    writer.writeheader()
    for data in results:
        writer.writerow(data)
    file_out.close()


if __name__ == '__main__':
    db.configure(Session)
    export_assignment()
    export_order()
