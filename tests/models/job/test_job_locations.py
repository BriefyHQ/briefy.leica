"""Test Jobs location database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestJobLocationModel(BaseModelTest):
    """Test JobLocation."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.JobAssignment, 'data/jobs.json'),
    ]
    file_path = 'data/job_locations.json'
    model = models.JobLocation
