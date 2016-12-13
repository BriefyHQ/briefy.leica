"""Test Tumblr link database model."""
from briefy.leica import models
from conftest import BaseLinkTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestTumblr(BaseLinkTest):
    """Test Tumblr database model."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]

    file_path = 'data/tumblr.json'
    model = models.Tumblr
