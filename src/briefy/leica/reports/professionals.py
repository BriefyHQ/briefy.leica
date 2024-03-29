"""Professionalss reports."""
from briefy.leica.models import Professional
from briefy.leica.models import ProfessionalBillingInfo
from briefy.leica.models import WorkingLocation
from briefy.leica.reports.base import BaseReport
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.query import Query

import typing as t


ASSIGNMENT_CSV = '/tmp/professionals.csv'


class AllProfessionals(BaseReport):
    """Report dumping all Professionals."""

    fieldnames = (
        'professional_display_name',
        'professional_legal_company_name',
        'professional_full_name',
        'professional_first_name',
        'professional_last_name',
        'professional_billing_street',
        'professional_billing_neighborhood',
        'professional_billing_city',
        'professional_billing_postcode',
        'professional_billing_country',
        'professional_billing_email',
        'professional_tax_status',
        'professional_tax_id_type',
        'professional_tax_id_name',
        'professional_tax_id',
        'professional_default_payment_method',
        'professional_second_payment_method',
        'professional_payment_email_paypal',
        'professional_payment_email_skrill',
        'professional_payment_bank_holder_name',
        'professional_payment_bank_iban',
        'professional_payment_bank_account_number',
        'professional_payment_bank_swift',
        'professional_payment_bank_name',
        'professional_payment_bank_street_address',
        'professional_payment_bank_city',
        'professional_payment_bank_country',
        'professional_id',
        'professional_location_1_city',
        'professional_location_1_region',
        'professional_location_1_country',
        'professional_location_2_city',
        'professional_location_2_region',
        'professional_location_2_country',
    )

    @property
    def _query_(self) -> Query:
        """Return the query for this report.

        :return: Query object.
        """
        return Professional.query().options(joinedload('billing_info'))

    @staticmethod
    def transform(record: Professional) -> dict:
        """Transform a record and result a record.

        :param record: Professional to be transformed.
        :return: Dictionary with data already transformed.
        """
        def extract_payment_info(info: ProfessionalBillingInfo) -> dict:
            """Extract payment information from a Professional Billing Information.

            :param info: Professional billing information.
            :return: Dictionary with payment information.
            """
            response = {
                'professional_default_payment_method': '',
                'professional_second_payment_method': '',
                'professional_payment_email_paypal': '',
                'professional_payment_email_skrill': '',
                'professional_payment_bank_holder_name': '',
                'professional_payment_bank_iban': '',
                'professional_payment_bank_account_number': '',
                'professional_payment_bank_swift': '',
                'professional_payment_bank_name': '',
                'professional_payment_bank_street_address': '',
                'professional_payment_bank_city': '',
                'professional_payment_bank_country': '',
            }
            if info:
                payment_info = billing_info.payment_info
                response[
                    'professional_default_payment_method'] = billing_info.default_payment_method
                response[
                    'professional_second_payment_method'] = billing_info.secondary_payment_method
                paypal_info = [i for i in payment_info if i['type_'] == 'paypal']
                if paypal_info:
                    response['professional_payment_email_paypal'] = paypal_info[0].get('email', '')
                skrill_info = [i for i in payment_info if i['type_'] == 'skrill']
                if skrill_info:
                    response['professional_payment_email_skrill'] = skrill_info[0].get('email', '')
                bank_info = [i for i in payment_info if i['type_'] == 'bank_account']
                if bank_info:
                    data = bank_info[0]
                    response.update(
                        {
                            'professional_payment_bank_holder_name': data['holder_name'],
                            'professional_payment_bank_iban': data['iban'],
                            'professional_payment_bank_account_number': data['account_number'],
                            'professional_payment_bank_swift': data['swift'],
                            'professional_payment_bank_name': data['bank_name'],
                            'professional_payment_bank_street_address': data['bank_street_address'],
                            'professional_payment_bank_city': data['bank_city'],
                            'professional_payment_bank_country': data['bank_country'],
                        }
                    )

            return response

        def extract_location_info(info: t.Sequence[WorkingLocation]) -> dict:
            """Extract payment information from a Professional Billing Information.

            :param info: Professional working location information.
            :return: Dictionary with location information.
            """
            location_1 = info[0].info if info and len(info) > 0 else {}
            location_2 = info[1].info if info and len(info) > 1 else {}
            response = {
                'professional_location_1_city': location_1.get('locality', ''),
                'professional_location_1_region': location_1.get('province', ''),
                'professional_location_1_country': location_1.get('country', ''),
                'professional_location_2_city': location_2.get('locality', ''),
                'professional_location_2_region': location_2.get('province', ''),
                'professional_location_2_country': location_2.get('country', ''),
            }
            return response

        legal_name = ''
        address = {}
        address_street = ''
        contact_first_name = record.first_name
        contact_last_name = record.last_name
        contact_name = f'{contact_first_name} {contact_last_name}'
        contact_email = record.email
        tax_id = ''
        tax_id_type = ''
        tax_id_name = ''
        tax_id_status = ''
        billing_info = record.billing_info
        locations = record.locations
        if billing_info:
            legal_name = billing_info.title
            address = billing_info.billing_address
            address_street = '{0} {1}'.format(
                address.get('route', ''),
                address.get('street_number', '')
            ).strip()

            contact_first_name = f'{billing_info.first_name}'
            contact_last_name = f'{billing_info.last_name}'
            contact_name = f'{contact_first_name} {contact_last_name}'
            contact_email = f'{billing_info.email}'
            tax_id = f'{billing_info.tax_id}'
            tax_id_type = f'{billing_info.tax_id_type.value}' if billing_info.tax_id_type else ''
            tax_id_name = f'{billing_info.tax_id_name}'
            tax_id_status = (
                f'{billing_info.tax_id_status.value}' if billing_info.tax_id_status else ''
            )

        payload = {
            'professional_id': record.id,
            'professional_display_name': record.title,
            'professional_legal_company_name': legal_name,
            'professional_full_name': contact_name,
            'professional_first_name': contact_first_name,
            'professional_last_name': contact_last_name,
            'professional_billing_street': address_street,
            'professional_billing_neighborhood': address.get('sublocality', ''),
            'professional_billing_city': address.get('locality', ''),
            'professional_billing_postcode': address.get('postal_code', ''),
            'professional_billing_country': address.get('country', ''),
            'professional_billing_email': contact_email,
            'professional_tax_status': tax_id_status,
            'professional_tax_id_type': tax_id_type,
            'professional_tax_id_name': tax_id_name,
            'professional_tax_id': tax_id,
        }
        payload.update(extract_payment_info(billing_info))
        payload.update(extract_location_info(locations))
        return payload
