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
    ]
    ignore_validation_fields = [
        'state_history', 'state', 'updated_at', 'customer', 'project', 'timezone',
        'customer_user', 'project_manager', 'scout_manager', 'location',
        'external_id', 'assignment', 'assignments', 'price', 'versions'
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
