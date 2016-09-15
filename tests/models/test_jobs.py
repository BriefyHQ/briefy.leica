"""Test Jobs database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestJobtModel(BaseModelTest):
    """Test Job."""

    dependencies = [
        (models.Project, 'data/projects.json')
    ]
    file_path = 'data/jobs.json'
    model = models.Job
