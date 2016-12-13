"""Test Portfolio database model."""
from briefy.leica import models
from conftest import BaseLinkTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestPortfolio(BaseLinkTest):
    """Test Porfolio database model."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]

    file_path = 'data/portfolio.json'
    model = models.Portfolio
    social = False
