"""Vocabularies used by Leica."""
from briefy.common.vocabularies import LabeledEnum


options = [
    ('undefined', 'undefined', 'undefined'),
    ('job_received', 'job_received', 'Job received'),
    ('in_scheduling_process', 'in_scheduling_process', 'In scheduling process'),
    ('scheduled', 'scheduled', 'Scheduled'),
    ('in_qa_process', 'in_qa_process', 'In QA process'),
    ('completed', 'completed', 'Completed'),
    ('in_revision_', 'in_revision_', 'In revision'),
    ('resolved', 'resolved', 'Resolved'),
]


ClientJobStatusChoices = LabeledEnum('ClientJobStatusChoices', options)


options = [
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


SchedulingIssuesChoices = LabeledEnum('SchedulingIssuesChoices', options)


options = [
    ('customer', 'customer', 'Input by Customer'),
    ('briefy', 'briefy', 'Input by Briefy'),
]


JobInputSource = LabeledEnum('JobInputSource', options)


options = [
    ('billing', 'billing', 'Billing contact'),
    ('business', 'business', 'Business contact'),
]


ContactTypes = LabeledEnum('ContactTypes', options)

options = [
    ('new', 'new', 'New'),
    ('returned_photographer', 'returned_photographer', 'Returned by Photographer'),
    ('refused_customer', 'refused_customer', 'Refused by Customer'),
]

TypesOfSetChoices = LabeledEnum('TypesOfSetChoices', options)
