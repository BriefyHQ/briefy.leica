from enum import Enum


class CategoryChoices(Enum):
    # TODO: Move to briefy.common
    undefined = 'undefined'
    accomodation = 'Accomnodation'
    food = 'Food'
    video = 'Video'
    company = 'Company'
    restaurant = 'Restaurant'


class ClientJobStatusChoices(Enum):
    undefined = 'undefined'
    job_received = 'Job received'
    in_scheduling_process = 'In scheduling process'
    scheduled = 'Scheduled'
    in_qa_process = 'In QA process'
    completed = 'Completed'
    in_revision_ = 'In revision '
    resolved = 'Resolved'


# class ApprovalStatusChoices(Enum):
    # awaiting_approval = 'Awaiting Approval'
    # approved = 'Approved'
    # not_approved = 'Not Approved'
    # updated_and_awaiting_for_approval = 'Updated And Awaiting For Approval'
    # awaiting_for_submission = 'Awaiting for submission'

class JobContinentChoices(Enum):
    undefined = 'undefined'
    europe = 'Europe'
    asia = 'Asia'
    north_america = 'North America'
    africa = 'Africa'
    caribbean = 'Caribbean'
    central_and_south_america = 'Central and South America'
    oceania = 'Oceania'
    antarctica = 'Antarctica'


class SchedulingIssuesChoices(Enum):
    undefined = 'undefined'
    owner_not_responding = 'A1. Owner not responding'
    rejected_by_owner_canceled = 'A2. Rejected by Owner / Canceled'
    owner_not_being_able_to_give_exact_dates = 'A3. Owner not being able to give exact dates'
    owner_not_aware_of_the_service = 'A4. Owner not aware of the service'
    unable_to_schedule_due_to_property_unavailability = 'B1. Unable to schedule due to' \
                                                        ' property unavailability (i.e. booked)'
    property_undergoing_renovation = 'B2. Property undergoing renovation'
    property_not_available_anymore = 'B3. Property not available anymore (i.e. sold)'
    property_in_bad_shape = 'B4. Property in bad shape'
    faulty_address_ = 'C1. Faulty address '
    faulty_contact_details_ = 'C2. Faulty contact details '
    weather_condition = 'C3. weather condition'
