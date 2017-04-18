"""Fix Orders and Assignments missing transitions.

Assignments: Approve, Refuse, Return to QA.
Orders: Deliver, Refuse, Require Revision.
"""
from briefy.leica.db import Session
from briefy.leica.models import Assignment
from briefy.leica.models import Order
from briefy.leica.sync.db import configure
from dateutil.parser import parse
from pprint import pprint

import csv
import pytz
import transaction


BASE_PATH = 'src/briefy/leica/tools/oneshots/data'
FIX_ASSIGNMENTS_TRANSITIONS_FNAME = BASE_PATH + '/Batch_April17_Fix_assignments_wrong_transitions.txt'  # noqa
ASSIGNMENTS_INSERT_TRANSITIONS = BASE_PATH + '/Batch_April17_Fix_assignments_missing_transitions.txt'  # noqa
FIX_DATES_FNAME = BASE_PATH + '/Batch_April17_Fix_wrong_transition_dates.txt'
ORDER_INSERT_TRANSITIONS = BASE_PATH + '/Batch_April17_Fix_missing_transitions_deliver_refuse_require-revision.txt'  # noqa
FIX_ORDER_TRANSITIONS_FNAME = BASE_PATH + '/Batch_April17_Fix_orders_wrong_transitions.txt'

ROLE_MAP = {
    'pm': 'project_manager',
    'qa': 'qa_manager',
    'customer': 'customer_user'
}

ORDER_ASSIGNMENT_TRANSITION = {
    'deliver': 'approve',
    'refuse': 'refuse',
    'require_revision': 'return_to_qa',
    'accept': 'complete',
    'start_qa': 'ready_for_upload',
}

ORDER_ASSIGNMENT_STATUS = {
    'delivered': 'approved',
    'refused': 'refused',
    'in_qa': 'in_qa',
    'accepted': 'completed'
}


def convert_date(date, dayfirst=True, berlin_zone=False):
    """Convert text date to datetime using mod::dateutil parse."""
    if dayfirst:
        date = parse(date, dayfirst=dayfirst)
    else:
        date = parse(date)

    if berlin_zone:
        tzinfo = pytz.timezone('Europe/Berlin')
        date = date.replace(tzinfo=tzinfo)
        date = date.astimezone(pytz.utc)
    else:
        date = date.replace(tzinfo=pytz.utc)
    return date


def find_user_by_role(order, role):
    """Find the user id based on the role name."""
    role = ROLE_MAP.get(role)
    if role == 'qa_manager':
        return getattr(order.assignments[0], role)
    else:
        return getattr(order, role)


def find_state_position(state_history, state, date):
    """Find the position to insert the new history record in the state_history."""
    position = None
    for i, item in enumerate(state_history):
        state_date = convert_date(item.get('date'), dayfirst=False).date()
        if item.get('to') == state and state_date <= date.date():
            position = i + 1
    return position


def insert_transition_order(order, item, date, debug=False, debug_duplicate=False):
    """Insert new transition in the Order state_history."""
    state_history = order.state_history
    previous_status = item.get('previous_order_status')
    position = find_state_position(state_history, previous_status, date)
    if position is None:
        if debug:
            message = 'Could not find position for Order id: {uid} ' \
                      'previous_status = {status} date = {date}'
            print(message.format(
                uid=order.id,
                status=previous_status,
                date=date
            ))
            return
    last_state = state_history[position - 1]['to']
    actor = find_user_by_role(order, item.get('user_role'))
    new_state = item.get('new_order_status')
    new_history = {
        'actor': str(actor),
        'date': date.isoformat(),
        'from': last_state,
        'to': new_state,
        'transition': item.get('transition_name'),
        'message': 'Inserted after migration: history fixing procedure.'
    }
    if position:
        try:
            current_history = state_history[position]
        except:
            current_history = None

        if (current_history and
            new_history['from'] == current_history['from'] and
            new_history['to'] == current_history['to'] and
            convert_date(
                new_history['date'], dayfirst=False).date() == convert_date(
                        current_history['date'], dayfirst=False).date()):
            if debug_duplicate:
                message = 'This transition already exists. \n Order: {current} : {new}'
                print(
                    message.format(
                        current=current_history,
                        new=new_history)
                )
            return

    state_history.insert(position, new_history)
    order.state_history = state_history.copy()
    order._update_dates_from_history()


def insert_transition_assignment(
        order,
        item,
        date,
        assignment_pos=0,
        debug=False,
        debug_duplicate=False):
    """Insert new transition in the Assignment state_history."""
    assignment = order.assignments[assignment_pos]
    state_history = assignment.state_history
    previous_status = ORDER_ASSIGNMENT_STATUS.get(item.get('previous_order_status'))
    position = find_state_position(state_history, previous_status, date)
    if position is None:
        if debug:
            message = 'Could not find position for Assignment. ' \
                      'Order id: {uid} Assignment id: {auid} ' \
                      'previous_status = {status} date = {date}'
            print(message.format(
                uid=order.id,
                auid=assignment.id,
                status=previous_status,
                date=date
            ))
        return

    last_state = state_history[position - 1]['to']
    actor = find_user_by_role(order, item.get('user_role'))
    new_state = ORDER_ASSIGNMENT_STATUS.get(item.get('new_order_status'))
    new_history = {
        'actor': str(actor),
        'date': date.isoformat(),
        'from': last_state,
        'to': new_state,
        'transition': ORDER_ASSIGNMENT_TRANSITION.get(item.get('transition_name')),
        'message': 'Inserted after migration: history fixing procedure.'
    }
    if position:
        try:
            current_history = state_history[position]
        except:
            current_history = None

        if (current_history and
            new_history['from'] == current_history['from'] and
            new_history['to'] == current_history['to'] and convert_date(
                new_history['date'], dayfirst=False).date() == convert_date(
                current_history['date'], dayfirst=False).date()):
            if debug_duplicate:
                message = 'This transition already exists. \nAssignment: {current} : {new}'
                print(
                    message.format(
                        current=current_history,
                        new=new_history)
                )
            return

    state_history.insert(position, new_history)
    assignment.state_history = state_history.copy()
    assignment._update_dates_from_history()


def read_tsv(fname):
    """Read tsv text file using DictReader."""
    with open(fname, 'r') as fin:
        reader = csv.DictReader(fin, delimiter='\t')
        for line_item in reader:
            yield line_item


def fix_order_date(order, position, item, debug=True):
    """Fix order transition date."""
    if debug:
        pprint(order.state_history[position])
    new_state_history = order.state_history.copy()
    new_date = item.get('new_date_time')
    new_date = convert_date(new_date, dayfirst=False)
    new_state_history[position]['date'] = new_date.isoformat()
    order.state_history = new_state_history
    if debug:
        pprint(order.state_history[position])
        pprint(item)


def fix_assignment_date(order, date, item, debug=True):
    """Fix assignment transition date."""
    assignment = order.assignment
    state_history = assignment.state_history
    previous_status = ORDER_ASSIGNMENT_STATUS.get(item.get('previous_order_status'))

    position = find_state_position(
        state_history,
        previous_status,
        date,
    )

    if debug:
        pprint(assignment.state_history[position])

    new_state_history = assignment.state_history.copy()
    new_date = item.get('new_date_time')
    new_date = convert_date(new_date, dayfirst=False)
    new_state_history[position]['date'] = new_date.isoformat()
    assignment.state_history = new_state_history

    if debug:
        pprint(assignment.state_history[position])
        pprint(item)


def fix_dates():
    """Fix orders and respective assignments state_history: date of transition."""
    for line_number, item in enumerate(read_tsv(FIX_DATES_FNAME)):
        uid = item.get('order_uid')
        date = item.get('current_date_time')
        date = convert_date(date, dayfirst=False)
        order = Order.get(uid)
        state_history = order.state_history
        previous_status = item.get('previous_order_status')
        position = find_state_position(
            state_history,
            previous_status,
            date
        )

        fix_order_date(order, position, item, debug=False)
        if len(order.assignments) == 1:
            try:
                fix_assignment_date(order, date, item, debug=False)
            except:
                message = 'Could not fix assignment for Order: {uid}\n' \
                          'Transition: {transition}. Assignment: {auid}'
                transition = item.get('transition_name')
                print(message.format(
                    uid=order.id,
                    auid=order.assignment.id,
                    transition=transition
                ))
        else:
            print('Order {uid} has {total} assignments.'.format(
                uid=order.id, total=len(order.assignments)
            ))

    transaction.commit()


def fix_orders_insert_transitions():
    """Fix orders and respective assignments state_history: insert missing transitions."""
    previous_item = None
    for line_number, item in enumerate(read_tsv(ORDER_INSERT_TRANSITIONS)):
        uid = item.get('order_uid')
        date = item.get('date_time')
        if not date:
            date = previous_item.get('date_time')
        date = convert_date(date, dayfirst=False)
        order = Order.get(uid)
        insert_transition_order(order, item, date, debug=True)
        if len(order.assignments) == 1:
            insert_transition_assignment(order, item, date, debug=True)
        else:
            # in this case second assignment should be used
            insert_transition_assignment(order, item, date, assignment_pos=1, debug=True)
        previous_item = item
    transaction.commit()


def fix_assignments_transitions(debug=False):
    """Fix assignments with wrong transitions."""
    for line_number, item in enumerate(read_tsv(FIX_ASSIGNMENTS_TRANSITIONS_FNAME)):
        uid = item.get('assignment_uid')
        date = item.get('date_time')
        date = convert_date(date, dayfirst=False)
        assignment = Assignment.get(uid)
        state_history = assignment.state_history
        previous_status = item.get('previous_assignment_status')
        position = find_state_position(
            state_history,
            previous_status,
            date
        )
        new_history = state_history.copy()
        if debug:
            pprint(item)
            pprint(new_history[position])
        new_history[position]['message'] = ''
        new_history[position]['transition'] = item.get('new_transition_name')
        new_history[position]['to'] = item.get('new_current_assignment_status')
        new_history[position]['date'] = convert_date(
            item.get('new_date_time'),
            dayfirst=False).isoformat()
        new_history[position]['actor'] = str(find_user_by_role(
            assignment.order,
            item.get('new_user_role'))
        )
        if debug:
            pprint(new_history[position])


def fix_assignments_insert_transitions(debug=False):
    """Fix assignments insert missing transitions."""
    for line_number, item in enumerate(read_tsv(ASSIGNMENTS_INSERT_TRANSITIONS)):
        uid = item.get('assignment_uid')
        date = item.get('date_time')
        date = convert_date(date, dayfirst=False)
        assignment = Assignment.get(uid)
        state_history = assignment.state_history.copy()
        previous_status = item.get('previous_assignment_status')
        position = find_state_position(
            state_history,
            previous_status,
            date
        )
        date = convert_date(item.get('date_time'), dayfirst=False)
        new_history = {
            'actor': str(find_user_by_role(assignment.order, item.get('user_role'))),
            'date': date.isoformat(),
            'from': previous_status,
            'to': item.get('new_assignment_status'),
            'transition': item.get('transition_name'),
            'message': 'Inserted after migration: history fixing procedure.'
        }
        if debug:
            pprint(item)
            pprint(new_history)

        state_history.insert(position, new_history)
        assignment.state_history = state_history


def fix_transitions_and_dates_orders(debug=False):
    """Fix orders state_history: update from state and date."""
    for line_number, item in enumerate(read_tsv(FIX_ORDER_TRANSITIONS_FNAME)):
        uid = item.get('order_uid')
        date = item.get('date_time')
        date = convert_date(date, dayfirst=False)
        order = Order.get(uid)
        state_history = order.state_history.copy()
        previous_status = item.get('previous_order_status')
        position = find_state_position(
            state_history,
            previous_status,
            date
        )
        position = position + 1
        if debug:
            pprint(item)
            pprint(state_history[position])
        state_history[position]['message'] = item.get('comment')
        state_history[position]['transition'] = item.get('new_transition_name')
        state_history[position]['to'] = item.get('new_order_status')
        state_history[position]['from'] = item.get('new_previous_order_status')
        state_history[position]['date'] = convert_date(
            item.get('new_date_time'),
            dayfirst=False).isoformat()
        state_history[position]['actor'] = str(find_user_by_role(order, item.get('new_user_role')))
        if debug:
            pprint(state_history[position])
        order.state_history = state_history


def fix_transitions_and_dates_assignments(debug=False):
    """Fix assignments state_history: update from state and date."""
    for line_number, item in enumerate(read_tsv(FIX_ORDER_TRANSITIONS_FNAME)):
        uid = item.get('order_uid')
        date = item.get('date_time')
        date = convert_date(date, dayfirst=False)
        order = Order.get(uid)
        assignment = order.assignments[-1]
        state_history = assignment.state_history.copy()
        previous_status = ORDER_ASSIGNMENT_STATUS.get(item.get('previous_order_status'))
        position = find_state_position(
            state_history,
            previous_status,
            date
        )
        position = position + 1
        if debug:
            pprint(item)
            pprint(state_history[position])
        state_history[position]['message'] = 'Update transition, status to, ' \
                                             'status from and date. history fixing procedure.'
        state_history[position]['transition'] = ORDER_ASSIGNMENT_TRANSITION.get(item.get('new_transition_name'))
        state_history[position]['to'] = ORDER_ASSIGNMENT_STATUS.get(item.get('new_order_status'))
        state_history[position]['from'] = ORDER_ASSIGNMENT_STATUS.get(item.get('new_previous_order_status'))
        state_history[position]['date'] = convert_date(
            item.get('new_date_time'),
            dayfirst=False).isoformat()
        state_history[position]['actor'] = str(find_user_by_role(order, item.get('new_user_role')))
        if debug:
            pprint(state_history[position])
        assignment.state_history = state_history


if __name__ == '__main__':
    configure(Session)
    with transaction.manager:
        fix_assignments_transitions()
        fix_assignments_insert_transitions()
        fix_dates()
        fix_orders_insert_transitions()
        fix_transitions_and_dates_orders()
        fix_transitions_and_dates_assignments()
