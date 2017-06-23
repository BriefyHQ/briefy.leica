"""Customer reports."""
from briefy.common.utilities.interfaces import IUserProfileQuery
from briefy.leica.models import Customer
from briefy.leica.reports.base import BaseReport
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.query import Query
from zope.component import getUtility


ASSIGNMENT_CSV = '/tmp/customers.csv'


class AllCustomers(BaseReport):
    """Report dumping all Customers."""

    fieldnames = (
        'customer_display_name',
        'customer_legal_name',
        'customer_billing_street_address',
        'customer_billing_neighborhood',
        'customer_billing_city',
        'customer_billing_postcode',
        'customer_billing_country',
        'customer_billing_contact_name',
        'customer_billing_contact_email',
        'customer_billing_contact_email2',
        'customer_tax_status',
        'customer_tax_id_type',
        'customer_tax_id_name',
        'customer_tax_id',
        'customer_bizdev_name',
        'customer_bizdev_email',
    )

    @property
    def _query_(self) -> Query:
        """Return the query for this report.

        :return: Query object.
        """
        return Customer.query().options(joinedload('billing_info'))

    @staticmethod
    def transform(record: Customer) -> dict:
        """Transform a record and result a record.

        :param record: Customer to be transformed.
        :return: Dictionary with data already transformed.
        """
        profile_service = getUtility(IUserProfileQuery)

        legal_name = ''
        address = {}
        address_street = ''
        contact_name = ''
        contact_email = ''
        tax_id = ''
        tax_id_type = ''
        tax_id_name = ''
        tax_id_status = ''
        bizdev_title = ''
        bizdev_email = ''

        billing_info = record.billing_info
        if billing_info:
            legal_name = billing_info.title
            address = billing_info.billing_address
            address_street = '{0} {1}'.format(
                address.get('route', ''),
                address.get('street_number', '')
            ).strip()

            contact_name = f'{billing_info.first_name} {billing_info.last_name}'
            contact_email = f'{billing_info.email}'
            tax_id = f'{billing_info.tax_id}'
            tax_id_type = f'{billing_info.tax_id_type.value}' if billing_info.tax_id_type else ''
            tax_id_name = f'{billing_info.tax_id_name}'
            tax_id_status = (
                f'{billing_info.tax_id_status.value}' if billing_info.tax_id_status else ''
            )

        bizdev = record.account_manager
        if bizdev:
            data = profile_service.get_data(str(bizdev))
            bizdev_title = data['fullname']
            bizdev_email = data['email']

        payload = {
            'customer_display_name': record.title,
            'customer_legal_name': legal_name,
            'customer_billing_street_address': address_street,
            'customer_billing_neighborhood': address.get('sublocality', ''),
            'customer_billing_city': address.get('locality', ''),
            'customer_billing_postcode': address.get('postal_code', ''),
            'customer_billing_country': address.get('country', ''),
            'customer_billing_contact_name': f'{contact_name}',
            'customer_billing_contact_email': f'{contact_email}',
            'customer_billing_contact_email2': '',
            'customer_tax_status': f'{tax_id_status}',
            'customer_tax_id_type': f'{tax_id_type}',
            'customer_tax_id_name': f'{tax_id_name}',
            'customer_tax_id': f'{tax_id}',
            'customer_bizdev_name': f'{bizdev_title}',
            'customer_bizdev_email': f'{bizdev_email}',
        }
        return payload
