"""Test AdditionalWorkingLocation database model."""
from briefy.leica import models
from conftest import BaseLocationTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestAdditionalWorkingLocation(BaseLocationTest):
    """Test Additional Working Location."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]
    file_path = 'data/additionalworkinglocation.json'
    model = models.AdditionalWorkingLocation
