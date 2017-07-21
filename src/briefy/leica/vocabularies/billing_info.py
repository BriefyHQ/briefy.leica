"""Billing information vocabularies."""
from briefy.common.vocabularies import LabeledEnum


__all__ = (
    'ContactTypes',
    'TaxIdStatusCustomers',
    'TaxIdStatusProfessionals',
    'TaxIdTypes',
)


contact_options = [
    ('billing', 'billing', 'Billing contact'),
    ('business', 'business', 'Business contact'),
]


ContactTypes = LabeledEnum('ContactTypes', contact_options)


tax_id_type = [
    ('1', '1', 'VAT/GST Reg. No'),
    ('2', '2', 'Tax Reg. No.'),
]

TaxIdTypes = LabeledEnum('TaxIdTypes', tax_id_type)


tax_id_professional_statuses = [
    ('11', '11', 'Germany - VAT Registered'),
    ('12', '12', 'Germany - VAT Exempt'),
    ('13', '13', 'Germany - Private Person'),
    ('21', '21', 'Europe Union - VAT Registered'),
    ('22', '22', 'Europe Union - VAT Exempt'),
    ('23', '23', 'Europe Union - Private Person'),
    ('31', '31', 'Rest of the World - VAT Registered'),
    ('32', '32', 'Rest of the World - VAT Exempt'),
    ('33', '33', 'Rest of the World - Private Person'),
]

TaxIdStatusProfessionals = LabeledEnum('TaxIdStatusProfessionals', tax_id_professional_statuses)


tax_id_customer_statuses = [
    ('11', '11', 'Germany - VAT Applicable'),
    ('21', '21', 'Europe Union - VAT Registered (Reverse charges)'),
    ('311', '311', 'Rest of the World - VAT Registered (Reverse charges)'),
    ('312', '312', 'Rest of the World - VAT Registered (No reverse charges)'),
]

TaxIdStatusCustomers = LabeledEnum('TaxIdStatusCustomers', tax_id_customer_statuses)
