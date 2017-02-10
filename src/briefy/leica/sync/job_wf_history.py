"""Import Job workflow history for Order and Assignment."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.leica import logger
from briefy.leica.models import Assignment
from briefy.leica.vocabularies import scheduling_options
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytz
import re


ms_laure_start = datetime(2016,11,1, 0,0,0,tzinfo=pytz.utc)
SCHEDULING = {i[2]: i[0] for i in scheduling_options}



# Field 'approval_status' on Knack.
# (Actually maps to several states on JobOrder and associated JobAssignments)
assignment_status = [
    ('Pending', 'pending'),
    ('Published', 'published'),
    ('Scheduled', 'scheduled'),
    ('Assigned', 'assigned'),
    ('Cancelled', 'cancelled'),
    ('Awaiting Assets', 'awaiting_assets'),
    ('Approved', 'approved'),
    ('Completed', 'completed'),
    ('Refused', 'refused'),
    ('In QA', 'in_qa'),
]

assignment_status_mapping = OrderedDict(assignment_status)


order_status = [
    ('Pending', 'received'),
    ('Published', 'received'),
    ('Scheduled', 'scheduled'),
    ('Assigned', 'assigned'),
    ('Cancelled', 'cancelled'),
    ('Awaiting Assets', 'scheduled'),
    ('Approved', 'delivered'),
    ('Completed', 'accepted'),
    ('Refused', 'refused'),
    ('In QA', 'in_qa'),
]

order_status_mapping = OrderedDict(order_status)


def _status_after_or_equal(status_to_check, reference_status):
    for knack_name, name in assignment_status_mapping:
        if name == status_to_check:
            return True
        elif name == reference_status:
            return False


def first(seq):
    """Return the first element of a sequence or None if it is empty."""
    if not seq:
        return None
    return next(iter(seq))


def _build_date(dt, minimal=None):
    """Return a safe str representation for a datetime.

    Given a valid datetime, or None and a valid minimal datetime,
    returns a valid str representation for it in i soformat-
    or the empty string.

    """
    if not dt and minimal:
        dt = minimal
    if dt:
        return dt.isoformat()
    return ''


def _get_identifier(kobj, field, default='Unknown'):
    """Retrieve the display name of given Knack relationship field."""
    attr = getattr(kobj, field, [])
    if not attr:
        return default
    return attr[0].get('identifier', default)


def parse_machine_log(kobj):
    """Parse machine log on Knack object."""
    history = []
    pattern = """(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.[\d]*:([^ ]*)"""
    matches = re.findall(pattern, kobj.machine_log)
    for item in matches:
        date = datetime(*[int(i) for i in item[0:-1]], tzinfo=timezone.utc)
        action = item[-1]
        message = 'This submission was {action}d by Briefy automatic system'.format(
            action=action
        )
        transition = 'invalidate_assets' if action == 'invalidate' else 'validate_assets'
        to_ = 'awaiting_assets' if action == 'invalidate' else 'in_qa'
        history.append(
            {
                'date': date,
                'message': message,
                'actor': str(SystemUser.id),
                'transition': transition,
                'from': 'asset_validation',
                'to': to_
            }
        )
    history.reverse()
    return history


def add_order_history(session, obj, kobj):
    """Add state_history and state information to the Order."""
    history = []
    knack_state = first(kobj.approval_status)
    if not knack_state:
        raise ValueError('Job without approval_status')
    order_state = order_status_mapping.get(knack_state)

    # created and received status
    person = _get_identifier(kobj, 'input_person', default='Briefy')
    actor_id = obj.project_manager if obj.source == 'briefy' else obj.customer_user
    actor = str(actor_id) if actor_id else str(SystemUser.id)
    history.append({
        'date': _build_date(kobj.input_date),
        'message': 'Created by {} on Knack database'.format(person),
        'actor': actor,
        'transition': '',
        'from': '',
        'to': 'created'
    })

    history.append({
        'date': _build_date(kobj.input_date),
        'message': 'Automatic transition to received',
        'actor': actor,
        'transition': 'submit',
        'from': 'created',
        'to': 'received'
    })
    last_date = kobj.input_date

    assignment = obj.assignment
    if not assignment:
        assignment = Assignment.query().filter(Assignment.order_id == obj.id).one()
    # check for 'assigned' status
    if kobj.assignment_date:
        person = _get_identifier(kobj, 'scouting_manager', default='Unknown')
        # actor should be assignment scout_manager if available
        actor_id = assignment.scout_manager
        actor = str(actor_id) if actor_id else str(SystemUser.id)
        history.append({
            'date': _build_date(kobj.assignment_date, last_date),
            'message': "Photographer assigned by '{}' on the Knack database".format(person),
            'actor': actor,
            'transition': 'assign',
            'from': 'received',
            'to': 'assigned'
        })
        last_date = kobj.assignment_date

    # check for 'scheduled' status
    if kobj.scheduled_shoot_date_time:
        date = kobj.scheduled_shoot_date_time
        if date in (kobj.availability_1, kobj.availability_2):
            person = _get_identifier(kobj, 'responsible_photographer', default='Photographer')
        else:
            person = 'Briefy'
        extra_message = ''
        if kobj.rescheduled:
            extra_message += (
                '''\nThis job was re-scheduled and may have been re-assigned/shot'''
                '''again. The old platform could not save this information. This transition'''
                '''refers to the last valid scheduling'''
            )

        # actor should be professional_user
        actor_id = assignment.professional_user
        actor = str(actor_id) if actor_id else str(SystemUser.id)
        history.append({
            'date': _build_date(date, last_date),
            'message': "Scheduled by '{}' on the Knack database".format(person) + extra_message,
            'actor': actor,
            'transition': 'schedule',
            'from': history[-1]['to'],
            'to': 'scheduled'
        })
        last_date = date

    # check for 'in_qa' status
    if kobj.submission_date:
        date = kobj.submission_date
        person = _get_identifier(kobj, 'responsible_photographer', default='Photographer')
        # actor should be professional_user
        actor_id = assignment.professional_user
        actor = str(actor_id) if actor_id else str(SystemUser.id)
        history.append({
            'date': _build_date(date, last_date),
            'message': "Submited by '{}' on the Knack database".format(person),
            'actor': actor,
            'transition': 'start_qa',
            'from': history[-1]['to'],
            'to': 'in_qa'
        })
        last_date = date

    # check for 'delivered' status
    if kobj.client_delivery_link.url:
        date = kobj.delivery_date_to_client or last_date
        person = _get_identifier(kobj, 'qa_manager', default='g:briefy_qa')
        # actor should be qa_manager
        actor_id = assignment.qa_manager
        actor = str(actor_id) if actor_id else 'g:briefy_qa'
        history.append({
            'date': _build_date(date, last_date),
            'message': "Delivered by '{}' on the Knack database".format(person),
            'actor': actor,
            'transition': 'deliver',
            'from': history[-1]['to'],
            'to': 'delivered'
        })
        last_date = date

    # check for 'accepted' status
    if knack_state.lower() == 'completed':
        date = kobj.last_approval_date or last_date
        # actor should be customer_user or project_manager
        actor_id = obj.customer_user or obj.project_manager
        actor = str(actor_id) if actor_id else str(SystemUser.id)
        history.append({
            'date': _build_date(date, last_date),
            'message': "Marked as  'completed' on the Knack database",
            'actor': actor,
            'transition': 'accept',
            'from': history[-1]['to'],
            'to': order_state
        })
        last_date = date

    # check for 'cancelled' status
    if knack_state.lower() == 'cancelled':
        date = kobj.last_approval_date or last_date
        # actor should be customer_user or project_manager
        actor_id = obj.customer_user or obj.project_manager
        actor = str(actor_id) if actor_id else str(SystemUser.id)
        history.append({
            'date': _build_date(date, last_date),
            'message': 'Job cancelled on the Knack database by unknown actor',
            'actor': actor,
            'transition': 'cancel',
            'from': history[-1]['to'],
            'to': order_state
        })
        last_date = date

    # check for 'refused' status
    if knack_state.lower() == 'refused':
        refuse_date = kobj.updated_at or kobj.delivery_date_to_client or last_date
        # actor should be customer_user or project_manager
        actor_id = obj.customer_user or obj.project_manager
        actor = str(actor_id) if actor_id else str(SystemUser.id)
        history.append({
            'date': _build_date(refuse_date, last_date),
            'message': 'Job refused by client',
            'actor': actor,
            'transition': 'refuse',
            'from': history[-1]['to'],
            'to': order_state
        })
        last_date = refuse_date

    obj.state_history = history
    # TODO: stick with knack actual status, last status history is not always accurate
    obj.state = order_state
    session.add(obj)
    model = obj.__class__.__name__
    logger.debug('{model} imported with state: {state}'.format(model=model, state=obj.state))


def add_assignment_history(session, obj, kobj, versions=()):
    """Add state_history and state information to the Assignment."""
    now = datetime_utcnow()
    dates = set()
    history = []
    order = obj.order
    knack_state = first(kobj.approval_status)
    if not knack_state:
        raise ValueError('Job without approval_status')
    assignment_state = assignment_status_mapping.get(knack_state)
    knack_state = knack_state.lower()

    # Initialize all dates
    created_at = kobj.input_date
    updated_at = kobj.updated_at
    assignment_date = kobj.assignment_date
    last_photographer_update = kobj.last_photographer_update
    last_approval_date = kobj.last_approval_date
    scheduled_shoot_date_time = kobj.scheduled_shoot_date_time
    availability = order.availability
    availability_1 = availability[0] if availability else None
    availability_2 = availability[1] if availability else None
    submission_date = kobj.submission_date
    delivery_date_to_client = kobj.delivery_date_to_client

    # Actors
    system_id = str(SystemUser.id)
    scout_manager = _get_identifier(kobj, 'scouting_manager', default='Unknown')
    input_person = _get_identifier(kobj, 'input_person', default='Briefy')
    professional = _get_identifier(kobj, 'responsible_photographer', default='Photographer')
    qa_manager = _get_identifier(kobj, 'qa_manager', default=system_id)

    # Check for 'created' status
    person = input_person
    actor_id = system_id if order.source == 'briefy' else order.customer_user
    actor = str(actor_id) if actor_id else system_id

    # Creation
    created_date = _build_date(created_at)
    history.append({
        'date': created_date,
        'message': 'Created by {0} on Knack database'.format(person),
        'actor': actor,
        'transition': '',
        'from': '',
        'to': 'created'
    })
    # First submission
    history.append({
        'date': created_date,
        'message': 'Automatic transition to pending',
        'actor': actor,
        'transition': 'submit',
        'from': 'created',
        'to': 'pending'
    })
    dates.add(created_at)
    last_date = created_at

    # Check for 'published' status
    if scout_manager.lower().strip() == 'job pool':
        # actor should be customer_user or project_manager
        actor_id = order.customer_user or order.project_manager
        actor = str(actor_id) if actor_id else system_id
        history.append({
            'date': created_date,
            'message': 'Assignment sent to pool',
            'actor': actor,
            'transition': 'publish',
            'from': 'pending',
            'to': 'published'
        })

    transition = ''
    if assignment_date:
        # Check for 'assigned' status
        person = scout_manager
        # actor should be professional_user or scout_manager
        is_job_pool = history[-1]['to'] == 'published'
        actor_id = obj.professional_user if is_job_pool else obj.scout_manager
        actor = str(actor_id) if actor_id else system_id
        assignment_date = assignment_date if assignment_date else created_at
        transition = 'assign' if not is_job_pool else 'self_assign'
        message = 'Photographer assigned by {0} on the Knack database'.format(person)
        if transition == 'self_assign':
            message = 'Photographer got the assignment from the Pool'
        history.append({
            'date': _build_date(assignment_date, created_at),
            'message': message,
            'actor': actor,
            'transition': transition,
            'from': history[-1]['to'],
            'to': 'assigned'
        })
        dates.add(assignment_date)
        last_date = assignment_date

    scheduling_issues = kobj.scheduling_issues
    if scheduling_issues:
        # actor should be customer_user or project_manager
        actor_id = obj.professional_user or order.project_manager
        actor = str(actor_id) if actor_id else system_id
        date = last_photographer_update or last_date
        message = str([i for i in scheduling_issues][0])
        history.append({
            'date': _build_date(date),
            'message': message,
            'actor': actor,
            'transition': 'scheduling_issues',
            'from': history[-1]['to'],
            'to': history[-1]['to']
        })
        dates.add(date)
        last_date = date

    #  Check for 'scheduled' status
    if scheduled_shoot_date_time:
        person = 'Briefy'
        if (
                (scheduled_shoot_date_time in (availability_1, availability_2)) or
                (transition == 'self_assign')
        ):
            person = professional

        # actor should be professional_user
        actor_id = obj.professional_user
        actor = str(actor_id) if actor_id else system_id
        history.append({
            'date': _build_date(assignment_date, last_date),
            'message': "Scheduled by '{0}' on the Knack database".format(person),
            'actor': actor,
            'transition': 'schedule',
            'from': history[-1]['to'],
            'to': 'scheduled'
        })
        dates.add(assignment_date)
        last_date = assignment_date

    #  Check for 'awaiting_assets' status
    if scheduled_shoot_date_time and now > scheduled_shoot_date_time:
        history.append({
            'date': _build_date(scheduled_shoot_date_time, last_date),
            'message': 'Waiting for asset upload (from data on Knack)',
            'actor': system_id,
            'transition': 'ready_for_upload',
            'from': 'scheduled',
            'to': 'awaiting_assets',
        })
        dates.add(scheduled_shoot_date_time)
        last_date = scheduled_shoot_date_time

    new_set = kobj.new_set
    submission_log = []
    if kobj.photo_submission_link and kobj.photo_submission_link.url:
        submission_log = parse_machine_log(kobj)
    if submission_log:
        actor_id = obj.professional_user
        actor = str(actor_id) if actor_id else system_id
        person = professional
        previous_state = ''
        previous_date = None
        for entry in submission_log:
            if last_approval_date and (last_approval_date < ms_laure_start) and not new_set:
                # There was at least a reproval here
                person = professional
                actor_id = obj.professional_user
                actor = str(actor_id) if actor_id else system_id
                date = _build_date(submission_date, last_date)
                history.append({
                    'date': date,
                    'message': "Submitted by '{0}' (from data on Knack)".format(person),
                    'actor': actor,
                    'transition': 'upload',
                    'from': 'awaiting_assets',
                    'to': 'asset_validation',
                })
                dates.add(date)
                date = submission_date
                history.append({
                    'date': _build_date(date, last_date),
                    'message': "Automatic validation skipped (from data on Knack)",
                    'actor': system_id,
                    'transition': 'validate_assets',
                    'from': 'asset_validation',
                    'to': 'in_qa',  # Note: can't know about intermediary non-validated sets
                })
                id_ = str(obj.qa_manager) or system_id
                history.append({
                    'date': date.isoformat(),
                    'message': "Rejected by '{0}' (from data on Knack)".format(qa_manager),
                    'actor': id_,
                    'transition': 'reject',
                    'from': 'in_qa',
                    'to': 'awaiting_assets',
                })
            if previous_state == 'in_qa':
                #  QA Manager must have refused this
                if last_approval_date and (entry['date'] > last_approval_date):
                    date = last_approval_date
                elif previous_date:
                    date = entry['date'] - timedelta(
                        ((entry['date'] - previous_date).seconds / 2) / 3600
                    )
                else:
                    date = entry['date'] - timedelta(1/1440)  # 1 minute before
                id_ = str(obj.qa_manager) or system_id
                history.append({
                    'date': date.isoformat(),
                    'message': "Rejected by '{0}' (from data on Knack)".format(qa_manager),
                    'actor': id_,
                    'transition': 'reject',
                    'from': 'in_qa',
                    'to': 'awaiting_assets',
                })
            history.append({
                'date': (entry['date'] - timedelta(1/1440)).isoformat(),
                'message': "Submitted by '{0}' (from data on Knack)".format(person),
                'actor': actor,
                'transition': 'upload',
                'from': 'awaiting_assets',
                'to': 'asset_validation',
            })
            dates.add(entry['date'])
            last_date = entry['date']
            previous_state = entry['to']
            previous_date = entry['date']
            entry['date'] = entry['date'].isoformat()
            history.append(entry)
    elif submission_date:
        person = professional
        # actor should be professional_user
        actor_id = obj.professional_user
        actor = str(actor_id) if actor_id else system_id
        date = _build_date(submission_date, last_date)
        history.append({
            'date': date,
            'message': "Submitted by '{0}' (from data on Knack)".format(person),
            'actor': actor,
            'transition': 'upload',
            'from': 'awaiting_assets',
            'to': 'asset_validation',
        })
        dates.add(date)
        date = submission_date
        history.append({
            'date': _build_date(date, last_date),
            'message': "Automatic validation skipped (from data on Knack)",
            'actor': system_id,
            'transition': 'validate_assets',
            'from': 'asset_validation',
            'to': 'in_qa',  # Note: can't know about intermediary non-validated sets
        })
        dates.add(date)
        last_date = date

    previous_state = history[-1]['to']
    if (last_approval_date and not new_set) and previous_state not in ('awaiting_assets', ):
        # TODO: Improve date checking here
        person = qa_manager
        actor_id = obj.qa_manager
        actor = str(actor_id) if actor_id else system_id
        date = last_approval_date or submission_date
        history.append({
            'date': _build_date(last_approval_date, last_date),
            'message': "Rejected by '{0}'".format(person),
            'actor': actor,
            'transition': 'reject',
            'from': 'in_qa',
            'to': 'awaiting_assets',
        })
        dates.add(date)
        last_date = date

    if delivery_date_to_client and (knack_state in ('approved', 'completed')):
        previous_state = history[-1]['to']
        if previous_state == 'awaiting_assets':
            person = professional
            # actor should be professional_user
            actor_id = obj.professional_user
            actor = str(actor_id) if actor_id else system_id
            date = last_photographer_update
            history.append({
                'date': _build_date(last_photographer_update, last_date),
                'message': "Submitted by '{0}' (from data on Knack)".format(person),
                'actor': actor,
                'transition': 'upload',
                'from': 'awaiting_assets',
                'to': 'asset_validation',
            })
            dates.add(date)
            history.append({
                'date': _build_date(date, last_date),
                'message': "Automatic validation skipped (from data on Knack)",
                'actor': system_id,
                'transition': 'validate_assets',
                'from': 'asset_validation',
                'to': 'in_qa',
            })
            last_date = date

        person = qa_manager
        # actor should be qa_manager
        actor_id = obj.qa_manager
        actor = str(actor_id) if actor_id else system_id
        date = delivery_date_to_client or last_approval_date or submission_date
        history.append({
            'date': _build_date(date, last_date),
            'message': "Approved by '{0}'".format(person),
            'actor': actor,
            'transition': 'approve',
            'from': 'in_qa',
            'to': 'approved',
        })
        dates.add(date)
        last_date = date

    # Check for 'refused' status
    if knack_state in ('refused', ):
        refuse_date = updated_at or delivery_date_to_client or last_approval_date or submission_date
        # project = obj.order.project.title
        # actor should be customer_user or project_manager
        actor_id = order.customer_user or order.project_manager
        actor = str(actor_id) if actor_id else system_id
        history.append({
            'date': _build_date(refuse_date, last_date),
            'message': "Set of photos refused by client",
            'actor': actor,
            'transition': 'refuse',
            'from': 'approved',
            'to': 'refused',
        })
        dates.add(refuse_date)
        last_date = refuse_date

    if knack_state in ('completed', ):
        # actor should be customer_user or project_manager
        actor_id = order.customer_user or order.project_manager
        actor = str(actor_id) if actor_id else system_id
        history.append({
            'date': _build_date(delivery_date_to_client, last_date),
            'message': "completed",
            'actor': actor,
            'transition': 'complete',
            'from': 'approved',
            'to': 'completed',
        })

    # Check for 'cancelled' status
    if knack_state == 'cancelled':
        date = last_approval_date or submission_date
        # actor should be customer_user or project_manager
        actor_id = order.customer_user or order.project_manager
        actor = str(actor_id) if actor_id else system_id
        history.append({
            # TODO: verify this date
            'date': _build_date(date, last_date),
            'message': "Cancelled by customer",
            'actor': actor,
            'transition': 'cancel',
            'from': history[-1]['to'],
            'to': assignment_state,
        })
        dates.add(date)
        last_date = date

    obj.state_history = history
    # TODO: stick with knack actual status, last status history is not always accurate
    obj.state = assignment_state
    session.add(obj)
    model = obj.__class__.__name__
    logger.debug('{model} imported with state: {state}'.format(model=model, state=obj.state))
