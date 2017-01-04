"""Test OrderLocation database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestOrderLocationModel(BaseModelTest):
    """Test OrderLocation."""

    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Order, 'data/orders.json'),
    ]
    file_path = 'data/order_locations.json'
    model = models.OrderLocation
