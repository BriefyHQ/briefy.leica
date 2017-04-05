import pytz
from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.models import Order
from briefy.leica.models import BriefyUserProfile
from briefy.leica.models import CustomerUserProfile
from briefy.leica.models import Professional
from dateutil.parser import parse
import transaction

fieldnames = ['uid', 'previous_order_status', 'transition_name', 'new_order_status', 'user_role', 'date_time', 'comment']
data = [
    ("fce461fa-c521-4bb7-884c-392dded8d77a", "in_qa", "deliver", "delivered", "qa", "11.01.2017", "first delivery", ),
    ("fce461fa-c521-4bb7-884c-392dded8d77a", "delivered", "refuse", "refused", "customer", "31.01.2017", "first refusal", ),
    ("fce461fa-c521-4bb7-884c-392dded8d77a", "refused", "require_revision", "in_qa", "pm", "", "sent back to QA_missing date", ),
    ("fce461fa-c521-4bb7-884c-392dded8d77a", "in_qa", "deliver", "delivered", "qa", "08.02.2017", "second delivery", ),
    ("fce461fa-c521-4bb7-884c-392dded8d77a", "delivered", "accept", "accepted", "customer", "14.02.2017", "acceptance", ),
    ("4d7bdda9-e9ac-44e5-8ce9-3ab619f34441", "in_qa", "deliver", "delivered", "qa", "07.12.2016", "first delivery", ),
    ("4d7bdda9-e9ac-44e5-8ce9-3ab619f34441", "delivered", "refuse", "refused", "customer", "21.12.2016", "first refusal", ),
    ("4d7bdda9-e9ac-44e5-8ce9-3ab619f34441", "refused", "require_revision", "in_qa", "pm", "", "sent back to QA_missing date", ),
    ("4d7bdda9-e9ac-44e5-8ce9-3ab619f34441", "in_qa", "deliver", "delivered", "qa", "10.01.2017", "second delivery", ),
    ("4d7bdda9-e9ac-44e5-8ce9-3ab619f34441", "delivered", "refuse", "refused", "customer", "16.02.2017", "second refusal", ),
    ("cd31225b-95c6-4b7d-bcae-67b1e75689bc", "in_qa", "deliver", "delivered", "qa", "02.12.2016", "first delivery", ),
    ("cd31225b-95c6-4b7d-bcae-67b1e75689bc", "delivered", "refuse", "refused", "customer", "20.12.2016", "first refusal", ),
    ("cd31225b-95c6-4b7d-bcae-67b1e75689bc", "refused", "require_revision", "in_qa", "pm", "", "sent back to QA_missing date", ),
    ("cd31225b-95c6-4b7d-bcae-67b1e75689bc", "in_qa", "deliver", "delivered", "qa", "10.02.2017", "second delivery", ),
    ("b3ea2f22-0b92-4f04-9fa6-a4b915fc74f2", "in_qa", "deliver", "delivered", "qa", "22.12.2016", "first delivery", ),
    ("b3ea2f22-0b92-4f04-9fa6-a4b915fc74f2", "delivered", "refuse", "refused", "customer", "11.01.2017", "first refusal", ),
    ("b3ea2f22-0b92-4f04-9fa6-a4b915fc74f2", "refused", "require_revision", "in_qa", "pm", "", "sent back to QA_missing date", ),
    ("b3ea2f22-0b92-4f04-9fa6-a4b915fc74f2", "in_qa", "deliver", "delivered", "qa", "08.02.2017", "second delivery", ),
    ("b3ea2f22-0b92-4f04-9fa6-a4b915fc74f2", "delivered", "refuse", "refused", "customer", "20.02.2017", "second refusal", ),
    ("cf6c20aa-f91a-428a-bb83-ce5e7224c5f8", "in_qa", "deliver", "delivered", "qa", "01.11.2016", "first delivery_in Leica", ),
    ("cf6c20aa-f91a-428a-bb83-ce5e7224c5f8", "delivered", "refuse", "refused", "customer", "10.01.2017", "first refusal_missing", ),
    ("cf6c20aa-f91a-428a-bb83-ce5e7224c5f8", "refused", "require_revision", "in_qa", "pm", "", "sent back to QA_missing date", ),
    ("cf6c20aa-f91a-428a-bb83-ce5e7224c5f8", "in_qa", "deliver", "delivered", "qa", "12.01.2017", "second delivery", ),
    ("cf6c20aa-f91a-428a-bb83-ce5e7224c5f8", "delivered", "refuse", "refused", "customer", "21.02.2017", "second refusal", ),
    ("d14d1499-d97f-4833-9697-e451a3ff3498", "in_qa", "deliver", "delivered", "qa", "14.11.2016", "first delivery_in Leica", ),
    ("d14d1499-d97f-4833-9697-e451a3ff3498", "delivered", "refuse", "refused", "customer", "07.12.2016", "first refusal_missing", ),
    ("d14d1499-d97f-4833-9697-e451a3ff3498", "refused", "require_revision", "in_qa", "pm", "", "sent back to QA_missing date", ),
    ("d14d1499-d97f-4833-9697-e451a3ff3498", "in_qa", "deliver", "delivered", "qa", "04.01.2017", "second delivery", ),
    ("95708c22-146f-4daa-9ddc-f619d704684d", "in_qa", "deliver", "delivered", "qa", "30.12.2016", "first delivery_in Leica", ),
    ("95708c22-146f-4daa-9ddc-f619d704684d", "delivered", "refuse", "refused", "customer", "05.01.2017", "first refusal_missing", ),
    ("95708c22-146f-4daa-9ddc-f619d704684d", "refused", "require_revision", "in_qa", "pm", "", "sent back to QA_missing date", ),
    ("95708c22-146f-4daa-9ddc-f619d704684d", "in_qa", "deliver", "delivered", "qa", "07.02.2017", "second delivery", ),
    ("95708c22-146f-4daa-9ddc-f619d704684d", "delivered", "refuse", "refused", "customer", "28.02.2017", "second refusal", ),
]


ROLE_MAP = {
    'pm': 'project_manager',
    'qa': 'qa_manager',
    'customer': 'customer_user'
}

ORDER_ASSIGNMENT_TRANSITION = {
    'deliver': 'approve',
    'refuse': 'refuse',
    'require_revision': 'return_to_qa',
    'accept': 'complete'
}

ORDER_ASSIGNMENT_STATUS = {
    'delivered': 'approved',
    'refused': 'refused',
    'in_qa': 'in_qa',
    'accepted': 'completed'
}


def convert_date(date, dayfirst=True, berlin_zone=False):
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


def find_user(user_name):
    user = BriefyUserProfile.query().filter(
        BriefyUserProfile.fullname == user_name
    ).one_or_none()
    if not user:
        user = CustomerUserProfile.query().filter(
            CustomerUserProfile.fullname == user_name
        ).one_or_none()
    if not user:
        user = Professional.query().filter(
            Professional.fullname == user_name
        ).one_or_none()
    if user:
        return str(user.id)
    else:
        return user_name


def find_user_by_role(order, role):
    role = ROLE_MAP.get(role)
    if role == 'qa_manager':
        return getattr(order.assignments[0], role)
    else:
        return getattr(order, role)


def find_state_position(state_history, state, date):
    position = None
    for i, item in enumerate(state_history):
        state_date = convert_date(item.get('date'), dayfirst=False).date()
        if item.get('to') == state and state_date <= date.date():
            position = i + 1
    return position


def get_previous_transition_date(order, position):
    return order.state_history[position].get('date')


def insert_transition_order(order, item, date):
    state_history = order.state_history
    previous_status = item.get('previous_order_status')
    position = find_state_position(state_history, previous_status, date)
    if position is None:
        print('Could not find position for Order id: {uid}'.format(uid=order.id))

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
            convert_date(new_history['date'], dayfirst=False).date() == convert_date(current_history['date'], dayfirst=False).date()):
            print('This transition already exists. \n Order: {current_history} : {new_history}'.format(
                current_history=current_history,
                new_history=new_history)
            )
            return

    state_history.insert(position, new_history)
    order.state_history = state_history.copy()
    order._update_dates_from_history()


def insert_transition_assignment(order, item, date):
    assignment = order.assignments[0]
    state_history = assignment.state_history
    previous_status = ORDER_ASSIGNMENT_STATUS.get(item.get('previous_order_status'))
    position = find_state_position(state_history, previous_status, date)
    if position is None:
        print('Could not find position for Assignment id: {uid}'.format(uid=assignment.id))

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
            print('This transition already exists. \n Assignment: {current_history} : {new_history}'.format(
                current_history=current_history,
                new_history=new_history)
            )
            return

    state_history.insert(position, new_history)
    assignment.state_history = state_history.copy()
    assignment._update_dates_from_history()


def main(data):
    for line_number, line in enumerate(data):
        item = {field: line[i] for i, field in enumerate(fieldnames)}
        uid = item.get('uid')
        date = item.get('date_time')
        if not date:
            previous_line = data[line_number - 1]
            previous_item = {field: previous_line[i] for i, field in enumerate(fieldnames)}
            date = previous_item.get('date_time')
        date = convert_date(date)
        order = Order.get(uid)
        insert_transition_order(order, item, date)
        if len(order.assignments) == 1:
            insert_transition_assignment(order, item, date)
        else:
            print('Order has {} assignments.'.format(len(order.assignments)))

    transaction.commit()


if __name__ == '__main__':
    configure(Session)
    main(data)
