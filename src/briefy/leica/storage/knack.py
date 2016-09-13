from briefy.leica.models import IJob

from zope.interface import Interface
from zope.component import adapts

KNACK_KEY = '_knack'


class IKnackObject(Interface):
    """Marker interface for objects comming from Knack database"""


class KnackJob:
    implements(IJob)
    adapts(IKnackObject)

    def __init__(self, knack_job):
        self.knack_job = knack_job

# Job Knack fields
"""
approval_status = {'label': 'Approval Status', 'type': 'multiple_choice', 'required': False, 'key': 'field_157', 'choices': ['Awaiting Approval', 'Approved', 'Not Approved', 'Updated And Awaiting For Approval', 'Awaiting for submission']}
assigned = {'label': 'Assigned', 'type': 'boolean', 'required': False, 'key': 'field_370'}
assignment_date = {'label': 'Assignment Date', 'type': 'date_time', 'required': False, 'key': 'field_226'}
availability_1 = {'label': 'Availability 1', 'type': 'date_time', 'required': False, 'key': 'field_427'}
availability_2 = {'label': 'Availability 2', 'type': 'date_time', 'required': False, 'key': 'field_428'}
category = {'label': 'Category', 'type': 'multiple_choice', 'required': False, 'key': 'field_107', 'choices': ['Accomodation', 'Food', 'Video', 'Company', 'Restaurant']}
client_delivery_link = {'label': 'Client Delivery Link', 'type': 'link', 'required': False, 'key': 'field_227'}
client_feedback = {'label': 'Client Feedback', 'type': 'paragraph_text', 'required': False, 'key': 'field_463'}
client_job_status = {'label': 'Client Job Status', 'type': 'multiple_choice', 'required': False, 'key': 'field_464', 'choices': ['Job received', 'In scheduling process', 'Scheduled', 'In QA process', 'Completed', 'In revision ', 'Resolved']}
client_specific_requirement = {'label': 'Client Specific Requirement', 'type': 'paragraph_text', 'required': False, 'key': 'field_423'}
company = {'label': 'Company', 'type': 'connection', 'required': False, 'relationship': {'object': 'object_21', 'has': 'one', 'belongs_to': 'many'}, 'key': 'field_528'}
contact_email = {'label': 'Contact Email', 'type': 'email', 'required': False, 'key': 'field_7'}
contact_number_1 = {'label': 'Contact Number 1', 'type': 'phone', 'required': False, 'key': 'field_6'}
contact_number_2 = {'label': 'Contact Number 2', 'type': 'phone', 'required': False, 'key': 'field_328'}
contact_person = {'label': 'Contact Person', 'type': 'name', 'required': False, 'key': 'field_5'}
currency_payout = {'label': 'Currency Payout', 'type': 'multiple_choice', 'required': False, 'key': 'field_358', 'choices': ['EUR', 'AUD', 'USD', 'GBP']}
finance_manager = {'label': 'Finance Manager', 'type': 'connection', 'required': False, 'relationship': {'object': 'object_18', 'has': 'many', 'belongs_to': 'many'}, 'key': 'field_371'}
finance_manager_to_payout = {'label': 'Finance Manager to Payout', 'type': 'connection', 'required': False, 'relationship': {'object': 'object_18', 'has': 'many', 'belongs_to': 'many'}, 'key': 'field_374'}
input_date = {'label': 'Input Date', 'type': 'date_time', 'required': False, 'key': 'field_209'}
input_person = {'label': 'Input Person', 'type': 'connection', 'required': False, 'relationship': {'object': 'object_4', 'has': 'one', 'belongs_to': 'many'}, 'key': 'field_369'}
input_source = {'label': 'Input source', 'type': 'multiple_choice', 'required': False, 'key': 'field_547', 'choices': ['Input by Picsajobs', 'Input by Client']}
internal_comments = {'label': 'Internal Comments', 'type': 'paragraph_text', 'required': False, 'key': 'field_487'}
internal_job_id = {'label': 'Internal Job ID', 'type': 'auto_increment', 'required': False, 'key': 'field_2'}
invoice_date = {'label': 'Invoice Date', 'type': 'date_time', 'required': False, 'key': 'field_373'}
job_continent = {'label': 'Job Continent', 'type': 'multiple_choice', 'required': False, 'key': 'field_210', 'choices': ['Europe', 'Asia', 'North America', 'Africa', 'Caribbean', 'Central and South America', 'Oceania']}
job_id = {'label': 'Job ID', 'type': 'short_text', 'required': False, 'key': 'field_109'}
job_location = {'label': 'Job Location', 'type': 'address', 'required': False, 'key': 'field_3'}
job_name = {'label': 'Job Name', 'type': 'short_text', 'required': False, 'key': 'field_212'}
last_approval_date = {'label': 'Last Approval Date', 'type': 'date_time', 'required': False, 'key': 'field_158'}
payout_date = {'label': 'Payout Date', 'type': 'date_time', 'required': False, 'key': 'field_372'}
photo_submission_link = {'label': 'Photo Submission Link', 'type': 'link', 'required': False, 'key': 'field_80'}
photographer_payout = {'label': 'Photographer Payout', 'type': 'number', 'required': False, 'key': 'field_72'}
photographers_comment = {'label': "Photographer's Comment", 'type': 'paragraph_text', 'required': False, 'key': 'field_155'}
project = {'label': 'Project', 'type': 'connection', 'required': False, 'relationship': {'object': 'object_20', 'has': 'one', 'belongs_to': 'many'}, 'key': 'field_414'}
project_manager_comment = {'label': 'Project Manager Comment', 'type': 'paragraph_text', 'required': False, 'key': 'field_548'}
qa_manager = {'label': 'QA Manager', 'type': 'connection', 'required': False, 'relationship': {'object': 'object_13', 'has': 'one', 'belongs_to': 'many'}, 'key': 'field_223'}
quality_assurance_feedback = {'label': 'Quality Assurance Feedback', 'type': 'paragraph_text', 'required': False, 'key': 'field_159'}
responsible_photographer = {'label': 'Responsible Photographer', 'type': 'connection', 'required': False, 'relationship': {'object': 'object_6', 'belongs_to': 'many', 'has': 'one'}, 'key': 'field_54'}
scheduled_shoot_date_time = {'label': 'Scheduled shoot Date/Time', 'type': 'date_time', 'required': False, 'key': 'field_73'}
scheduling_issues = {'label': 'Scheduling Issues', 'type': 'multiple_choice', 'required': False, 'key': 'field_79', 'choices': ['', 'A1. Owner not responding', 'A2. Rejected by Owner / Canceled', 'A3. Owner not being able to give exact dates', 'A4. Owner not aware of the service', 'B1. Unable to schedule due to property unavailability (i.e. booked)', 'B2. Property undergoing renovation', 'B3. Property not available anymore (i.e. sold)', 'B4. Property in bad shape', 'C1. Faulty address ', 'C2. Faulty contact details ', 'C3. weather condition']}
scouting_manager = {'label': 'Scouting Manager', 'type': 'connection', 'required': False, 'relationship': {'object': 'object_14', 'belongs_to': 'many', 'has': 'one'}, 'key': 'field_327'}
set_price = {'label': 'Set Price', 'type': 'number', 'required': False, 'key': 'field_452'}
signed_releases_contract = {'label': 'Signed Releases Contract', 'type': 'file', 'required': False, 'key': 'field_498'}
submission_date = {'label': 'Submission Date', 'type': 'date_time', 'required': False, 'key': 'field_160'}
travel_expenses = {'label': 'Travel Expenses', 'type': 'number', 'required': False, 'key': 'field_161'}
update_completed = {'label': 'Update Completed', 'type': 'boolean', 'required': False, 'key': 'field_228'}


"""
