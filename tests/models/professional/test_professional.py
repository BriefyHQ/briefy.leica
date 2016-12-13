"""Test Professional database model."""
from briefy.leica import models
from conftest import BaseModelTest


class TestProfessionalModel(BaseModelTest):
    """Test Professional."""

    file_path = 'data/professionals.json'
    model = models.Professional
