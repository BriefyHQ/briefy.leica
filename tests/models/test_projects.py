"""Test Project database model."""
from briefy.leica.models import Project
from conftest import BaseModelTest


class TestProjectModel(BaseModelTest):
    """Test Project."""

    file_path = 'data/projects.json'
    model = Project
