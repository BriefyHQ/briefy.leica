"""Vocabularies used by Leica."""
from briefy.common.vocabularies import LabeledEnum


order_type = [
    ('order', 'order', 'Order'),
    ('leadorder', 'leadorder', 'LeadOrder'),
]

OrderTypeChoices = LabeledEnum('OrderTypeChoices', order_type)

order_options = [
    ('undefined', 'undefined', 'undefined'),
    ('job_received', 'job_received', 'Job received'),
    ('in_scheduling_process', 'in_scheduling_process', 'In scheduling process'),
    ('scheduled', 'scheduled', 'Scheduled'),
    ('in_qa_process', 'in_qa_process', 'In QA process'),
    ('completed', 'completed', 'Completed'),
    ('in_revision_', 'in_revision_', 'In revision'),
    ('resolved', 'resolved', 'Resolved'),
]


OrderStatusChoices = LabeledEnum('OrderStatusChoices', order_options)


scheduling_options = [
    ('undefined', 'undefined', 'undefined'),
    ('owner_not_responding', 'owner_not_responding', 'A1. Owner not responding'),
    (
        'rejected_by_owner_canceled',
        'rejected_by_owner_canceled',
        'A2. Rejected by Owner / Canceled'
    ),
    (
        'owner_not_being_able_to_give_exact_dates',
        'owner_not_being_able_to_give_exact_dates',
        'A3. Owner not being able to give exact dates'
    ),
    (
        'owner_not_aware_of_the_service',
        'owner_not_aware_of_the_service',
        'A4. Owner not aware of the service'
    ),
    (
        'property_unavailability',
        'property_unavailability',
        'B1. Unable to schedule due to property unavailability (i.e. booked)'
    ),
    ('undergoing_renovation', 'undergoing_renovation', 'B2. Property undergoing renovation'),
    ('not_available_anymore', 'not_available_anymore',
     'B3. Property not available anymore (i.e. sold)'),
    ('in_bad_shape', 'in_bad_shape', 'B4. Property in bad shape'),
    ('faulty_address', 'faulty_address', 'C1. Faulty address '),
    ('faulty_contact_details', 'faulty_contact_details', 'C2. Faulty contact details '),
    ('weather_condition', 'weather_condition', 'C3. weather condition'),
]


SchedulingIssuesChoices = LabeledEnum('SchedulingIssuesChoices', scheduling_options)


input_options = [
    ('customer', 'customer', 'Input by Customer'),
    ('briefy', 'briefy', 'Input by Briefy'),
]


OrderInputSource = LabeledEnum('OrderInputSource', input_options)


contact_options = [
    ('billing', 'billing', 'Billing contact'),
    ('business', 'business', 'Business contact'),
]


ContactTypes = LabeledEnum('ContactTypes', contact_options)


types_options = [
    ('new', 'new', 'New Set'),
    ('returned_photographer', 'returned_photographer', 'Returned by Photographer'),
    ('refused_customer', 'refused_customer', 'Refused by Customer'),
]

TypesOfSetChoices = LabeledEnum('TypesOfSetChoices', types_options)


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


asset_types = [
    ('Image', 'Image', 'Image'),
    ('ImageRaw', 'ImageRaw', 'Raw Image'),
    ('Video', 'Video', 'Video'),
    ('Cinemagraph', 'Cinemagraph', 'Cinemagraph'),
    ('Matterport', 'Matterport', 'Matterport'),
]

AssetTypes = LabeledEnum('AssetTypes', asset_types)
