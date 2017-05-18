"""Test Orders view."""
from briefy.common.db import datetime_utcnow
from briefy.leica import models
from conftest import BaseVersionedTestView
from datetime import timedelta

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestOrderView(BaseVersionedTestView):
    """Test OrderService view."""

    base_path = '/orders'
    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
    ]
    ignore_validation_fields = [
        'state_history', 'state', 'updated_at', 'customer', 'project', 'timezone',
        'customer_user', 'project_manager', 'scout_manager', 'location',
        'external_id', 'assignment', 'assignments', 'price', 'versions'
    ]
    file_path = 'data/orders.json'
    model = models.Order
    initial_wf_state = 'received'
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'title': 'New Order Title changed!',
        'price': 10000,
        'price_currency': 'USD',
        'availability': [
            (datetime_utcnow() + timedelta(days=14)).isoformat(),
            (datetime_utcnow() + timedelta(days=21)).isoformat()
        ]
    }

    def test_put_invalid_asset_type(self, app, obj_payload):
        """Asset type should match one of the possible values."""
        payload = obj_payload
        del(payload['availability'])
        obj_id = payload['id']
        payload['asset_types'] = ['Foobar']
        request = app.put_json('{base}/{id}'.format(base=self.base_path, id=obj_id),
                               payload, headers=self.headers, status=400)
        result = request.json
        error = result['errors'][0]
        assert result['status'] == 'error'
        assert error['name'] == 'asset_types'
        assert error['location'] == 'body'
        assert 'Invalid type of asset' in error['description']

    def test_put_invalid_number_of_asset_types(self, app, obj_payload):
        """Asset type supports only 1 item."""
        payload = obj_payload
        obj_id = payload['id']
        payload['asset_types'] = ['Image', 'Matterport']
        request = app.put_json('{base}/{id}'.format(base=self.base_path, id=obj_id),
                               payload, headers=self.headers, status=400)
        result = request.json
        error = result['errors'][0]
        assert result['status'] == 'error'
        assert error['name'] == 'asset_types'
        assert error['location'] == 'body'
        assert 'Invalid number of type of assets' in error['description']
