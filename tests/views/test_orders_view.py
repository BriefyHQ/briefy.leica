"""Test Orders view."""
from briefy.leica import models
from conftest import BaseVersionedTestView
from datetime import datetime
from datetime import timedelta

import pytest
import pytz


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
        'external_id', 'assignment', 'assignments'
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
            str(datetime.now(tz=pytz.utc) + timedelta(days=14)),
            str(datetime.now(tz=pytz.utc) + timedelta(days=21))
        ]
    }
