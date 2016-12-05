"""Test MainWorkingLocation database model."""
from briefy.leica import models
from conftest import BaseLocationTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestMainWorkingLocation(BaseLocationTest):
    """Test Main Working Location."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]
    file_path = 'data/mainworkinglocation.json'
    model = models.MainWorkingLocation
