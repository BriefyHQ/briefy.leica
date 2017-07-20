"""Test Order Charge validation."""
from briefy.leica.models.job.order import OrderCharge
from briefy.leica.models.job.order import OrderCharges

import colander
import pytest


valid_data = (
    ('rescheduling', 1200, '', '669a99c2-9bb3-443f-8891-e600a15e3c10', '', '', ''),
    ('cancellation', 0, 'Foo bar', '669a99c2-9bb3-443f-8891-e600a15e3c10', '', '', ''),
    ('model_release', 123000, '20 people', '669a99c2-9bb3-443f-8891-e600a15e3c10', '', '', ''),
    ('property_release', 3000, 'Owner signed', '669a99c2-9bb3-443f-8891-e600a15e3c10', '', '', ''),
    ('other', 3000, 'Other reason', '669a99c2-9bb3-443f-8891-e600a15e3c10', '', '', ''),
    ('other', 3000, 'Other reason', '669a99c2-9bb3-443f-8891-e600a15e3c10', '', '', ''),
)


@pytest.mark.parametrize('data', valid_data)
def test_order_charge_serialization(data):
    """Test successful OrderCharge serialization."""
    payload = {
        'category': data[0], 'amount': data[1], 'reason': data[2], 'created_by': data[3],
        'id': data[4], 'invoice_number': data[5], 'invoice_date': data[6],
    }
    schema = OrderCharge()
    response = schema.deserialize(payload)
    assert response['category'] == payload['category']
    assert response['amount'] == payload['amount']
    assert response['reason'] == payload['reason']
    assert response['created_by'] == payload['created_by']
    assert response['id'] is not None


wrong_data = (
    ('wrong_reason', 1200, '', '669a99c2-9bb3-443f-8891-e600a15e3c10'),
    ('work', 'wrong', 'Foo bar', '669a99c2-9bb3-443f-8891-e600a15e3c10'),
    ('work', 123000, 123, '669a99c2-9bb3-443f-8891-e600a15e3c10'),
    ('work', 123000, '', 'meu_login'),
)


@pytest.mark.parametrize('data', wrong_data)
def test_order_charge_serialization_failure(data):
    """Test failed OrderCharge serialization."""
    payload = {'category': data[0], 'amount': data[1], 'reason': data[2], 'created_by': data[3]}
    schema = OrderCharge()
    with pytest.raises(colander.Invalid):
        schema.deserialize(payload)


valid_charges = (
    valid_data,
)


@pytest.mark.parametrize('data', valid_charges)
def test_order_charges_serialization(data):
    """Test successful OrderCharges serialization."""
    payload = [
        {'category': i[0], 'amount': i[1], 'reason': i[2], 'created_by': i[3]}
        for i in data
    ]
    schema = OrderCharges()
    response = schema.deserialize(payload)
    assert len(response)
    assert response[0]['category'] == payload[0]['category']
    assert response[0]['amount'] == payload[0]['amount']
    assert response[0]['reason'] == payload[0]['reason']
    assert response[0]['created_by'] == payload[0]['created_by']
    assert response[0]['id'] is not None


invalid_charges = (
    wrong_data,
)


@pytest.mark.parametrize('data', invalid_charges)
def test_order_charges_serialization_failure(data):
    """Test failed OrderCharges serialization."""
    payload = [
        {'category': i[0], 'amount': i[1], 'reason': i[2], 'created_by': i[3]}
        for i in data
    ]
    schema = OrderCharges()
    with pytest.raises(colander.Invalid):
        schema.deserialize(payload)
