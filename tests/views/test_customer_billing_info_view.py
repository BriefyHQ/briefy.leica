"""Test Customer Billing Info view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestCustomerBillingInfo(BaseTestView):
    """Test Billing Info for an Asset."""

    base_path = (
        '/billing_info/customers'
    )
    dependencies = [
        (models.Customer, 'data/customers.json'),
    ]
    file_path = 'data/customer_billing_infos.json'
    ignore_validation_fields = ['customer', 'state_history']
    model = models.CustomerBillingInfo
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'email': 'billing@customer.briefy.co'
    }
