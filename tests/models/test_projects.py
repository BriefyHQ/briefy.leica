"""Test Project database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestProjectModel(BaseModelTest):
    """Test Project."""

    dependencies = [
        (models.Customer, 'data/customers.json'),
    ]
    file_path = 'data/projects.json'
    model = models.Project
