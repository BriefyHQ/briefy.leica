"""Export all data for finance invoice."""
from briefy.leica.db import Session
from briefy.leica.models import Assignment
from briefy.leica.models import Order
from briefy.leica.sync import db
from briefy.leica.utils.transitions import get_transition_date_from_history
from collections import OrderedDict

import csv

ORDER_CSV = '/tmp/orders.csv'
ASSIGNMENT_CSV = '/tmp/orders.csv'


def export_order():
    """Export all orders to csv file."""
    all = Order.query().all()
    results = []
    for item in all:
        state_history = item.state_history
        last_refusal_date = get_transition_date_from_history(
            ('refuse',), state_history, first=False,
        )
        accept_date = get_transition_date_from_history(
            ('accept',), state_history, first=True,
        )
        if item.location:
            street = item.location.info.get('route')
            number = item.location.info.get('street_number')
            locatity = item.location.locality
            country = item.location.country.code
        else:
            street = ''
            number = ''
            locatity = ''
            country = ''

        if item.assignments:
            assignment = item.assignments[-1]
            submission_date = assignment.submission_date
            submission_path = assignment.submission_path
        else:
            submission_date = None
            submission_path = None

        payload = OrderedDict(
            project_name=item.project.title,
            category=item.category.value,
            input_date=item.created_at,
            source=item.source.value,
            uid=item.id,
            briefy_id=item.slug,
            customer_order_id=item.customer_order_id,
            order_name=item.title,
            street='{0}, {1}'.format(street, number),
            locatity=locatity,
            country=country,
            number_required_assets=item.number_required_assets,
            scheduled_datetime=item.scheduled_datetime,
            submission_date=submission_date,
            subimission_path=submission_path,
            status=item.state,
            delivery_date=item.deliver_date,
            last_deliver_date=item.last_deliver_date,
            delivery=item.delivery.get('gdrive') if item.delivery else '',
            last_refusal_date=last_refusal_date,
            accept_date=accept_date,
            price_currency=item.price_currency,
            price=item.price
        )
        results.append(payload)
        print('Order appended: {id}'.format(id=item.id))
    file_out = open(ORDER_CSV, 'w')
    fieldnames = results[0].keys()
    writer = csv.DictWriter(file_out, fieldnames=fieldnames)
    writer.writeheader()
    for data in results:
        writer.writerow(data)
    file_out.close()


def export_assignment():
    """Export all assignment to csv file."""
    all = Assignment.query().all()
    results = []
    file_out = open(ASSIGNMENT_CSV, 'w')
    for item in all:
        payload = OrderedDict(
            """
            Project Name
            Category (from the Order)
            UID
            Briefy ID
            Customer Order ID (from Order)
            Assignment Name
            Assignment Location: City
            Assignment Location: Country
            Number of Assets (from the Order)
            Responsible Photographer: title
            Assignment Status
            Set type
            Scheduled Shoot Date/Time
            Last Submission Date
            Photo Submission Link
            Last Approval Date
            Last Refusal Date
            Accept Date
            Currency Payout
            Photographer Payout
            Travel Expenses
            Additional Compensation
            Reason for Additional Compensation
            """
        )
        results.append(payload)

    fieldnames = results[0].keys()
    writer = csv.DictWriter(file_out, fieldnames=fieldnames)
    writer.writeheader()
    for data in results:
        writer.writerow(data)
    file_out.close()


if __name__ == '__main__':
    db.configure(Session)
    # export_assignment()
    export_order()
