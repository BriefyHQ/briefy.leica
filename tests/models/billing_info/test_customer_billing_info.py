"""Test Customer Billing Info database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestCustomerBillingInfoModel(BaseModelTest):
    """Test CustomerBillingInfo."""

    dependencies = [
        (models.Customer, 'data/customers.json'),
    ]
    file_path = 'data/customer_billing_infos.json'
    model = models.CustomerBillingInfo
