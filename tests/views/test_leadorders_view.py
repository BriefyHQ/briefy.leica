"""Test Orders view."""
from briefy.common.db import datetime_utcnow
from briefy.leica import models
from conftest import BaseVersionedTestView
from datetime import timedelta

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestLeadOrderView(BaseVersionedTestView):
    """Test LeadOrderService view."""

    base_path = '/orders'
    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.CustomerUserProfile, 'data/customer_profiles.json'),
        (models.InternalUserProfile, 'data/internal_profiles.json')
    ]
    serialize_attrs = [
        'path', '_roles', '_actors', 'customer', 'project', 'timezone', 'assignment', 'assignments'
    ]
    ignore_validation_fields = [
        'state_history', 'state', 'location'
    ]
    file_path = 'data/leadorders.json'
    model = models.LeadOrder
    initial_wf_state = 'new'
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'title': 'New LeadOrder Title changed!',
        'price': 10000,
        'price_currency': 'USD',
        'availability': [
            (datetime_utcnow() + timedelta(days=14)).isoformat(),
            (datetime_utcnow() + timedelta(days=21)).isoformat()
        ]
    }

    def test_unsuccessful_creation(self, obj_payload, app):
        """Test unsuccessful creation of a new model."""
        payload = obj_payload
        payload['id'] = 'e93b5902-c15e-4b47-8e01-a93df6ea7211'
        # Use a project that does not allow creation of new orders
        payload['project_id'] = '4a068a1b-3646-4acf-937d-15563853e388'
        request = app.post_json(self.base_path, payload, headers=self.headers, status=403)

        assert request.status_code == 403
        result = request.json
        assert result['status'] == 'error'
        assert result['message'] == 'Unauthorized'
