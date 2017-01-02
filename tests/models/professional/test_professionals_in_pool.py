"""Test ProfessionalsInPool database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestProfessionalsInPoolModel(BaseModelTest):
    """Test ProfessionalsInPoll."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.JobOrder, 'data/job_orders.json'),
        (models.JobPool, 'data/job_pools.json'),
    ]
    file_path = 'data/professionals_in_pool.json'
    model = models.ProfessionalsInPool
