"""Test Instagram link database model."""
from briefy.leica import models
from conftest import BaseLinkTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestInstagram(BaseLinkTest):
    """Test Instagram database model."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]

    file_path = 'data/instagram.json'
    model = models.Instagram
