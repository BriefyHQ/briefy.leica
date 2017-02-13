"""Test Customer database model."""
from briefy.leica import models
from conftest import BaseModelTest


class TestCustomerModel(BaseModelTest):
    """Test Customer."""

    file_path = 'data/customers.json'
    model = models.Customer
