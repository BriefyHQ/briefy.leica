"""Helpers to validate and fix state_history."""
from briefy.leica import logger
from briefy.leica.db import Session
from briefy.leica.models import Assignment
from briefy.leica.models import Customer
from briefy.leica.models import CustomerUserProfile
from briefy.leica.models import InternalUserProfile
from briefy.leica.models import Item
from briefy.leica.models import LeadOrder
from briefy.leica.models import Order
from briefy.leica.models import Photographer
from briefy.leica.models import Pool
from briefy.leica.models import Project
from operator import itemgetter

import transaction
import typing as t


def get_all_items(types: tuple) -> t.List[t.Tuple]:
    """Create a list with all items: id, type, state and state_history."""
    return Session.query(
        Item.id, Item.type, Item.state, Item._state_history
    ).filter(Item.type.in_(types))


def count_wrong(state_history: t.List[dict], state: str) -> int:
    """Count the total of transitions in the wrong position."""
    total = len(state_history)
    total_wrong = 0
    for i, transition in enumerate(state_history):
        if i == 0 and transition.get('to') != 'created':
            total_wrong = total_wrong + 1
            continue
        if 1 <= i < total:
            previous = state_history[i-1]
            if transition.get('from') != previous.get('to'):
                total_wrong = total_wrong + 1
                continue
        if i == total and transition.get('to') != state:
            total_wrong = total_wrong + 1
            continue
    return total_wrong


def find_wrong(state_history: t.List[dict], state: str, skip: list) -> int:
    """Find transition in the wrong position."""
    wrong_position = None
    total = len(state_history)
    for i, transition in enumerate(state_history):
        if i in skip:
            continue
        if i == 0 and transition.get('to') != 'created':
            wrong_position = i
            break
        if 1 <= i < total:
            previous = state_history[i-1]
            if transition.get('from') != previous.get('to'):
                wrong_position = i
                break
        if i == total and transition.get('to') != state:
            wrong_position = i
            break
    return wrong_position


def sort_state_history(state_history: t.List[dict]) -> t.List[dict]:
    """Sort by date state history."""
    return sorted(state_history, key=itemgetter('date'))


def fix_transition_position(
        state_history: t.List[dict],
        position: int
) -> t.Tuple[t.List[dict], bool]:
    """Move transition from one position to another and return the updated state history."""
    state_history = state_history.copy()
    to_fix = state_history.pop(position)
    fixed = False
    for i, transition in enumerate(state_history):
        tto = transition.get('to')
        tdate = transition.get('date')
        if to_fix.get('from') == tto and to_fix.get('date') >= tdate:
            state_history.insert(i + 1, to_fix)
            fixed = True
            break
    if not fixed:
        state_history.insert(position, to_fix)
    return state_history, fixed


def fix_state_history(
        types: tuple,
        model: Item,
        debug: bool=False
) -> t.Tuple[list, list, list, int]:
    """Fix state history."""
    model_name = model.__name__
    items_fixed = []
    items_skiped = []
    items_loop = []
    all_items = get_all_items(types).all()
    total = len(all_items)
    for id_, type_, state, state_history in all_items:
        skip = []
        number_fixed = 0
        total_wrong = count_wrong(state_history, state)
        if not total_wrong:
            continue
        new_state_history = sort_state_history(state_history)
        number_transitions = len(new_state_history)
        wrong_position = find_wrong(new_state_history, state, skip)
        while wrong_position is not None and number_fixed < number_transitions:
            if debug:
                logger.debug(f'Starting fixing model {model_name} id: {id_}')
            new_state_history, fixed = fix_transition_position(new_state_history, wrong_position)
            if not fixed:
                not_fixed = state_history[wrong_position]
                logger.debug(f'Transition not fixed for {model_name} id: {id_} '
                             f'\ntransition:{not_fixed}\n')
                skip.append(wrong_position)
            else:
                number_fixed = number_fixed + 1
            wrong_position = find_wrong(new_state_history, state, skip)
        if number_fixed >= number_transitions:
            items_loop.append(id_)
            logger.debug(f'Loop detected for {model_name} id: {id_}')
        if skip:
            items_skiped.append(id_)
        if number_fixed or total_wrong:
            obj = model.get(id_)
            obj.state_history = new_state_history
            items_fixed.append(id_)
    return items_fixed, items_skiped, items_loop, total


def fix_customers_wrong_transition():
    """Fix all wrong transitions in customers."""
    for o in Customer.query().all():
        state_history = o.state_history.copy()
        for item in state_history:
            if item.get('transition') == 'activate':
                item['to'] = 'active'
        o.state_history = state_history
        session = o.__session__
        session.flush()


def fix_leads_wrong_transition():
    """Fix all wrong transitions in leadorders."""
    with transaction.manager:
        types = ('leadorder', )
        for id_, type_, state, state_history in get_all_items(types):
            fixed = False
            new_state_history = sort_state_history(state_history)
            for i, item in enumerate(new_state_history):
                if item.get('to') == 'new':
                    previous_to = new_state_history[i - 1].get('to')
                    if item['from'] != previous_to:
                        item['from'] = previous_to
                        fixed = True
                        logger.debug(f'Fixing for LeadOder id: {id_} transition to new.')
            if fixed:
                obj = LeadOrder.get(id_)
                obj.state_history = new_state_history


def report_issues(types: tuple):
    """Execute the main report."""
    good_before = []
    good_after = []
    worst = []
    better = []
    same = []
    other = []
    query = get_all_items(types)
    total_items = query.count()
    total_sorted_wrong = 0
    total_wrong = 0
    for id_, type_, state, state_history in query:
        wrong = count_wrong(state_history, state)
        sorted_state_history = sort_state_history(state_history)
        sorted_wrong = count_wrong(sorted_state_history, state)
        if 0 < sorted_wrong < wrong:
            better.append(id_)
            total_wrong = total_wrong + wrong
            total_sorted_wrong = total_sorted_wrong + sorted_wrong
        elif sorted_wrong == wrong and sorted_wrong > 0:
            same.append(id_)
        elif 0 < wrong < sorted_wrong:
            worst.append(id_)
        else:
            if wrong == 0:
                good_before.append(id_)
            elif sorted_wrong == 0:
                good_after.append(id_)
            else:
                other.append(id_)

    total_good_before = len(good_before)
    total_good_after = len(good_after)
    total_worst = len(worst)
    total_better = len(better)
    total_same = len(same)
    total_other = len(other)
    avg_wrong = total_wrong / total_items
    avg_sorted_wrong = total_sorted_wrong / total_items

    print(f'========={types}===========')
    print(f'Good before: {total_good_before}')
    print(f'Good after: {total_good_after}')
    print(f'Worst: {total_worst}')
    print(f'Better: {total_better}')
    print(f'Same: {total_same}')
    print(f'Other: {total_other}')
    print(f'Total Items: {total_items}')
    print(f'Avg wrong: {avg_wrong}')
    print(f'Avg sorted_wrong: {avg_sorted_wrong}')


def main():
    """Verify and fix the state history for all the main types."""
    models = [
        ('customer', Customer, fix_customers_wrong_transition, False),
        ('photographer', Photographer, None, False),
        ('project', Project, None, False),
        ('customeruserprofile', CustomerUserProfile, None, False),
        ('pool', Pool, None, None),
        ('internaluserprofile', InternalUserProfile, None, False),
        ('leadorder', LeadOrder, fix_leads_wrong_transition, False),
        ('order', Order, None, False),
        ('assignment', Assignment, None, False),
    ]
    for type_, model, fix_before, debug in models:
        with transaction.manager:
            model_name = model.__name__
            print(f'Fixing model: {model_name}')
            if fix_before:
                fix_before()
            fixed, skip, loop, total = fix_state_history((type_,), model, debug=debug)
            total_fixed = len(fixed)
            total_skip = len(skip)
            total_loop = len(loop)
            print(f'Total of items: {total}')
            print(f'Total fixed: {total_fixed}')
            print(f'Total skip: {total_skip}')
            print(f'Total loop: {total_loop}')
            print('\n')


if __name__ == '__main__':
    main()
