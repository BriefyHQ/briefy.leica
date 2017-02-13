"""Test Youtube link database model."""
from briefy.leica import models
from conftest import BaseLinkTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestYoutube(BaseLinkTest):
    """Test Youtube database model."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]

    file_path = 'data/youtube.json'
    model = models.Youtube
