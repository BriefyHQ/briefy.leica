"""Import Job workflow history for Order and Assignment."""
from briefy.leica import logger
from briefy.leica.models import UserProfile
from collections import OrderedDict
from datetime import datetime

import pytz

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
    actor = str(actor_id) if actor_id else 'g:system'
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

    # check for 'assigned' status
    if kobj.assignment_date:
        person = _get_identifier(kobj, 'scouting_manager', default='Unknown')
        # actor should be assignment scout_manager if available
        actor_id = obj.assignments[0].scout_manager
        actor = str(actor_id) if actor_id else 'g:system'
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
        actor_id = obj.assignments[0].professional_user
        actor = str(actor_id) if actor_id else 'g:system'
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
        actor_id = obj.assignments[0].professional_user
        actor = str(actor_id) if actor_id else 'g:system'
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
        date = kobj.last_approval_date or last_date
        person = _get_identifier(kobj, 'qa_manager', default='g:briefy_qa')
        # actor should be qa_manager
        actor_id = obj.assignments[0].qa_manager
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
        actor = str(actor_id) if actor_id else 'g:system'
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
        actor = str(actor_id) if actor_id else 'g:system'
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
        date = kobj.delivery_date_to_client or last_date
        # actor should be customer_user or project_manager
        actor_id = obj.customer_user or obj.project_manager
        actor = str(actor_id) if actor_id else 'g:system'
        history.append({
            'date': _build_date(date, last_date),
            'message': 'Job refused by client',
            'actor': actor,
            'transition': 'refuse',
            'from': history[-1]['to'],
            'to': order_state
        })
        last_date = date

    obj.state_history = history
    # TODO: stick with knack actual status, last status history is not always accurate
    obj.state = order_state
    session.add(obj)
    model = obj.__class__.__name__
    logger.debug('{model} imported with state: {state}'.format(model=model, state=obj.state))


def add_assignment_history(session, obj, kobj):
    """Add state_history and state information to the Assigment."""
    history = []
    order = obj.order
    knack_state = first(kobj.approval_status)
    if not knack_state:
        raise ValueError('Job without approval_status')
    assignment_state = assignment_status_mapping.get(knack_state)

    # Check for 'created' status
    person = _get_identifier(kobj, 'input_person', default='Briefy')
    actor_id = obj.order.project_manager if \
            obj.order.source == 'briefy' else obj.order.customer_user
    actor = str(actor_id) if actor_id else 'g:system'
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
        'message': 'Automatic transition to pending',
        'actor': actor,
        'transition': 'submit',
        'from': 'created',
        'to': 'pending'
    })
    last_date = kobj.input_date

    # Check for 'published' status
    if _get_identifier(kobj, 'scouting_manager').lower().strip() == 'job pool':
        # actor should be customer_user or project_manager
        actor_id = order.customer_user or order.project_manager
        actor = str(actor_id) if actor_id else 'g:system'
        history.append({
            'date': _build_date(kobj.input_date),
            'message': 'Assignment sent to job pool',
            'actor': actor,
            'transition': 'publish',
            'from': 'pending',
            'to': 'published'
        })

    # Check for 'assigned' status
    if kobj.assignment_date:
        person = _get_identifier(kobj, 'scouting_manager', default='Unknown')
        # actor should be professional_user or scout_manager
        is_job_pool = history[-1]['to'] == 'published'
        actor_id = obj.professional_user if is_job_pool else obj.scout_manager
        actor = str(actor_id) if actor_id else 'g:system'
        history.append({
            'date': _build_date(kobj.assignment_date, kobj.input_date),
            'message': "Photographer assigned by '{}' on the Knack database".format(person),
            'actor': actor,
            'transition': 'assign' if not is_job_pool else 'self_assign',
            'from': history[-1]['to'],
            'to': 'assigned'
        })
        last_date = kobj.assignment_date

    #  Check for 'scheduled' status
    if kobj.scheduled_shoot_date_time:
        date = kobj.scheduled_shoot_date_time
        if date in (kobj.availability_1, kobj.availability_2):
            person = _get_identifier(kobj, 'responsible_photographer', default='Photographer')
        else:
            person = 'Briefy'

        # actor should be professional_user
        actor_id = obj.professional_user
        actor = str(actor_id) if actor_id else 'g:system'
        history.append({
            'date': _build_date(date, last_date),
            'message': "Scheduled by '{0}' on the Knack database".format(person),
            'actor': actor,
            'transition': 'schedule',
            'from': history[-1]['to'],
            'to': 'scheduled'
        })
        last_date = date

    #  Check for 'awaiting_assets' status
    dt = kobj.scheduled_shoot_date_time
    if dt and datetime.now(tz=pytz.UTC) > dt:
        history.append({
            'date': _build_date(kobj.scheduled_shoot_date_time, last_date),
            'message': 'Waiting for asset upload (from data on Knack)',
            'actor': 'g:system',
            'transition': 'ready_for_upload',
            'from': 'scheduled',
            'to': 'awaiting_assets',
        })
        last_date = kobj.scheduled_shoot_date_time

    # Check for Validation status: # TODO currently broken on the knack workflow.
    if kobj.submission_date:
        person = _get_identifier(kobj, 'responsible_photographer', default='Photographer')
        # actor should be professional_user
        actor_id = obj.professional_user
        actor = str(actor_id) if actor_id else 'g:system'
        history.append({
            'date': _build_date(kobj.submission_date, last_date),
            'message': "Submited by '{}' (from data on Knack)".format(person),
            'actor': actor,
            'transition': 'upload',
            'from': 'awaiting_assets',
            'to': 'validation',
        })
        last_date = kobj.submission_date

    # Check for 'in_qa' status
    if kobj.submission_date:
        date = kobj.last_approval_date or kobj.submission_date
        history.append({
            'date': _build_date(date, last_date),
            'message': "Automatic validation skipped (from data on Knack)",
            'actor': 'g:system',
            'transition': 'validate',
            'from': 'validation',
            'to': 'in_qa',  # Note: can't know about intermediary non-validated sets
        })
        last_date = date

    # TODO: check if job was returned back to awaiting assets (EDIT NEEDED)

    # Check for 'approved' status
    if knack_state.lower() == 'approved':
        person = _get_identifier(kobj, 'qa_manager', default='g:briefy_qa')
        # actor should be qa_manager
        actor_id = obj.qa_manager
        actor = str(actor_id) if actor_id else 'g:briefy_qa'
        date = kobj.last_approval_date or kobj.submission_date
        history.append({
            'date': _build_date(kobj.submission_date, last_date),
            'message': "Approved by '{}'".format(person),
            'actor': actor,
            'transition': 'approve',
            'from': 'in_qa',
            'to': assignment_state,
        })
        last_date = date

    if knack_state.lower() == 'completed':
        # actor should be customer_user or project_manager
        actor_id = order.customer_user or order.project_manager
        actor = str(actor_id) if actor_id else 'g:system'
        history.append({
            'date': _build_date(kobj.submission_date, last_date),
            'message': "completed",
            'actor': actor,
            'transition': 'complete',
            'from': 'approved',
            'to': assignment_state,
        })

    # Check for 'cancelled' status
    if knack_state.lower() == 'cancelled':
        date = kobj.last_approval_date or kobj.submission_date
        # actor should be customer_user or project_manager
        actor_id = order.customer_user or order.project_manager
        actor = str(actor_id) if actor_id else 'g:system'
        history.append({
            # TODO: verify this date
            'date': _build_date(kobj.submission_date, last_date),
            'message': "Cancelled by customer",
            'actor': actor,
            'transition': 'cancel',
            'from': history[-1]['to'],
            'to': assignment_state,
        })

    # Check for 'refused' status
    if knack_state.lower() == 'refused':
        date = kobj.last_approval_date or kobj.submission_date
        project = _get_identifier(kobj, 'customer')
        # actor should be customer_user or project_manager
        actor_id = order.customer_user or order.project_manager
        actor = str(actor_id) if actor_id else 'g:system'
        history.append({
            # TODO: verify this date
            'date': _build_date(kobj.submission_date, last_date),
            'message': "Set of photos refused by client from project '{}'".format(project),
            'actor': actor,
            'transition': 'refuse',
            'from': 'approved',
            'to': assignment_state,
        })

    obj.state_history = history
    # TODO: stick with knack actual status, last status history is not always accurate
    obj.state = assignment_state
    session.add(obj)
    model = obj.__class__.__name__
    logger.debug('{model} imported with state: {state}'.format(model=model, state=obj.state))
