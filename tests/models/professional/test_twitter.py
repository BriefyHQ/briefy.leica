"""Test Twitter link database model."""
from briefy.leica import models
from conftest import BaseLinkTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestTwitter(BaseLinkTest):
    """Test Twitter database model."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]

    file_path = 'data/twitter.json'
    model = models.Twitter
