"""Order Vocabularies."""
from briefy.common.vocabularies import LabeledEnum


__all__ = (
    'OrderChargesChoices',
    'OrderInputSource',
    'OrderStatusChoices',
    'OrderTypeChoices',
)


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


input_options = [
    ('customer', 'customer', 'Input by Customer'),
    ('briefy', 'briefy', 'Input by Briefy'),
]


OrderInputSource = LabeledEnum('OrderInputSource', input_options)


order_charges = [
    ('model_release', 'Model release'),
    ('property_release', 'Property release'),
    ('cancellation', 'Cancellation fee'),
    ('rescheduling', 'Rescheduling fee'),
    ('other', 'Other'),
]


OrderChargesChoices = LabeledEnum('OrderCharges', order_charges)
