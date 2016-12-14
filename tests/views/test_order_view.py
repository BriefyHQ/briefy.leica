"""Test jobs view."""
from briefy.leica import models
from conftest import BaseVersionedTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestJobOrderView(BaseVersionedTestView):
    """Test JobOrderService view."""

    base_path = '/orders'
    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
    ]
    ignore_validation_fields = [
        'state_history', 'state', 'updated_at', 'customer', 'project',
        'qa_manager', 'project_manager', 'scout_manager',
    ]
    file_path = 'data/job_orders.json'
    model = models.JobOrder
    initial_wf_state = 'received'
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'title': 'New Order Title changed!',
        'price': 10000,
        'price_currency': 'USD'
    }
