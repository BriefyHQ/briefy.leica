"""Test charges utilities."""
from briefy.leica.utils import charges
from briefy.ws.errors import ValidationError

import pytest


base_value = [
    {
        'id': '9ea38889-4056-42f3-9eaa-d582efb4d718',
        'category': 'model_release',
        'amount': 1200,
        'reason': '10 people',
        'created_at': '2017-07-20T16:22:31.404667+00:00',
        'created_by': '669a99c2-9bb3-443f-8891-e600a15e3c10',
        'invoice_number': '',
        'invoice_date': '',
    },
    {
        'id': '29168c8e-2b6b-4dac-8eaf-714e161ee16c',
        'category': 'other',
        'amount': 2000,
        'reason': 'Another fee',
        'created_at': '2017-07-20T16:22:31.404667+00:00',
        'created_by': '669a99c2-9bb3-443f-8891-e600a15e3c10',
        'invoice_number': '',
        'invoice_date': '',
    }
]

empty_value = []


def test_order_charges_update_delete_all():
    """Test order_charges_update function, deleting existing charges."""
    func = charges.order_charges_update

    current_value = base_value
    new_value = empty_value

    value = func(current_value, new_value)
    assert isinstance(value, list)
    assert len(value) == 0


new_line = [
    {
        'id': '',
        'category': 'other',
        'amount': 3000,
        'reason': 'Yet another fee',
        'created_at': '',
        'created_by': '669a99c2-9bb3-443f-8891-e600a15e3c10',
        'invoice_number': '',
        'invoice_date': '',
    }
]


def test_order_charges_add_charge():
    """Test order_charges_update function, adding a new charge."""
    func = charges.order_charges_update

    current_value = base_value
    new_value = base_value + new_line

    value = func(current_value, new_value)
    assert isinstance(value, list)
    assert len(value) == 3
    # Added an id
    assert value[-1]['id'] != ''
    # Added a created_at
    assert value[-1]['created_at'].endswith('+00:00')


def test_order_charges_update_charge():
    """Test order_charges_update function, updating an existing charge."""
    func = charges.order_charges_update

    current_value = base_value
    new_value = [d.copy() for d in base_value]
    new_value[-1]['invoice_number'] = '1DEF1'
    new_value[-1]['invoice_date'] = '2017-07-21'

    value = func(current_value, new_value)
    assert isinstance(value, list)
    assert len(value) == 2

    assert value[-1]['invoice_number'] == new_value[-1]['invoice_number']
    assert value[-1]['invoice_date'] == new_value[-1]['invoice_date']


def test_order_charges_update_charge_convert_invoice_date():
    """Test order_charges_update function, updating an existing charge."""
    from datetime import date

    func = charges.order_charges_update

    current_value = base_value
    new_value = [d.copy() for d in base_value]
    new_value[-1]['invoice_number'] = '1DEF1'
    new_value[-1]['invoice_date'] = date(2017, 7, 21)

    value = func(current_value, new_value)
    assert isinstance(value, list)
    assert len(value) == 2

    assert value[-1]['invoice_number'] == new_value[-1]['invoice_number']
    assert value[-1]['invoice_date'] == new_value[-1]['invoice_date']


def test_order_charges_update_not_overwrite_created_at_created_by():
    """Test order_charges_update function, updating an existing charge will not update created."""
    func = charges.order_charges_update

    current_value = base_value
    new_value = [d.copy() for d in base_value]
    new_value[-1]['created_at'] = '2017-07-20T16:22:31.404667+01:00'
    new_value[-1]['created_by'] = '9f19964c-0302-47bc-aa0a-08ba506f909d'

    value = func(current_value, new_value)
    assert isinstance(value, list)
    assert len(value) == 2

    assert value[-1]['created_at'] == current_value[-1]['created_at']
    assert value[-1]['created_by'] == current_value[-1]['created_by']
    assert value[-1]['created_at'] != new_value[-1]['created_at']
    assert value[-1]['created_by'] != new_value[-1]['created_by']


def test_order_charges_update_validation_error_on_invoiced_charge():
    """Test order_charges_update function, trying to delete an invoiced charge."""
    func = charges.order_charges_update

    current_value = [d.copy() for d in base_value]
    current_value[-1]['invoice_number'] = '1DEF1'
    current_value[-1]['invoice_date'] = '2017-07-21'

    new_value = base_value[:-1]

    with pytest.raises(ValidationError) as exc:
        func(current_value, new_value)
    assert 'Not possible to delete an already invoiced item.' in str(exc)
