"""Test Order database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestOrderModel(BaseModelTest):
    """Test Order."""

    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json')
    ]
    file_path = 'data/orders.json'
    model = models.Order
    initial_wf_state = 'received'
