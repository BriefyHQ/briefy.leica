"""Test customers view."""
from briefy.leica import models
from conftest import BaseTestView


class TestCustomerView(BaseTestView):
    """Test CustomerService view."""

    base_path = '/customers'
    file_path = 'data/customers.json'
    model = models.Customer
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    initial_wf_state = 'pending'
    update_map = {
        'title': 'New Customer Name',
        'description': 'New Customer Description',
    }
