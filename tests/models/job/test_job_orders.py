"""Test JobOrder database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestJobOrderModel(BaseModelTest):
    """Test JobOrder."""

    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json')
    ]
    file_path = 'data/job_orders.json'
    model = models.JobOrder
    initial_wf_state = 'received'
