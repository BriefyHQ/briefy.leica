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

    def test_get_collection_custom_filter_customer_deliveries(self, app, login_as_customer):
        """Test get a collection of items using custom filters."""
        user_payload, token = login_as_customer
        headers = self.headers
        headers['Authorization'] = f'JWT {token}'
        request = app.get('{base}?_custom_filter=customer_deliveries'.format(base=self.base_path),
                          headers=headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == len(result['data'])

    def test_get_collection_custom_filter_late_first_submission(self, app):
        """Test get a collection of items using custom filters."""
        request = app.get('{base}?_custom_filter=late_first_submission'.format(base=self.base_path),
                          headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == len(result['data'])

    def test_get_collection_custom_filter_late_re_submission(self, app):
        """Test get a collection of items using custom filters."""
        request = app.get('{base}?_custom_filter=late_re_submission'.format(base=self.base_path),
                          headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == len(result['data'])

    def test_put_invalid_additional_charges(self, app, obj_payload):
        """Deal with invalid values sent to additional_charges."""
        payload = obj_payload.copy()
        del(payload['availability'])
        obj_id = payload['id']
        payload['additional_charges'] = """[
            {
                "category": "wrong",
                "amount": 1200,
                "reason": "",
                "created_by": "669a99c2-9bb3-443f-8891-e600a15e3c10"
            }
        ]"""
        request = app.put_json('{base}/{id}'.format(base=self.base_path, id=obj_id),
                               payload, headers=self.headers, status=400)
        result = request.json
        error = result['errors'][0]
        assert result['status'] == 'error'
        assert error['name'] == 'additional_charges'
        assert error['location'] == 'body'
        assert 'Invalid payload for additional_charges' in error['description']

    def test_put_valid_additional_charges(self, app, obj_payload):
        """Updating additional_charges should also update total_order_price."""
        payload = obj_payload.copy()
        del(payload['availability'])
        obj_id = payload['id']
        payload['additional_charges'] = """[
            {
                "category": "other",
                "amount": 12000,
                "reason": "A good reason",
                "created_by": "669a99c2-9bb3-443f-8891-e600a15e3c10"
            }
        ]"""
        request = app.put_json('{base}/{id}'.format(base=self.base_path, id=obj_id),
                               payload, headers=self.headers, status=200)
        result = request.json
        additional_charges = result['additional_charges']
        assert len(additional_charges) == 1
        assert additional_charges[0]['amount'] == 12000
        assert additional_charges[0]['category'] == 'other'
        assert result['total_order_price'] == result['actual_order_price'] + 12000

    def test_put_invalid_asset_type(self, app, obj_payload):
        """Asset type should match one of the possible values."""
        payload = obj_payload.copy()
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
        payload = obj_payload.copy()
        del(payload['availability'])
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

    def test_unsuccessful_creation(self, obj_payload, app):
        """Test unsuccessful creation of a new model."""
        payload = obj_payload.copy()
        del(payload['availability'])
        payload['id'] = 'e93b5902-c15e-4b47-8e01-a93df6ea7211'
        # Use a project that does not allow creation of new orders
        payload['project_id'] = '4a068a1b-3646-4acf-937d-15563853e388'
        request = app.post_json(self.base_path, payload, headers=self.headers, status=403)

        assert request.status_code == 403
        result = request.json
        assert result['status'] == 'error'
        assert result['message'] == 'Unauthorized'
