"""Test Facebook link database model."""
from briefy.leica import models
from conftest import BaseLinkTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestFacebook(BaseLinkTest):
    """Test Facebook database model."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]

    file_path = 'data/facebook.json'
    model = models.Facebook
