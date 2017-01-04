"""Test Comment database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestCommentModel(BaseModelTest):
    """Test Comment."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Order, 'data/orders.json'),
        (models.Assignment, 'data/assignments.json'),
        (models.Image, 'data/images.json'),
    ]
    file_path = 'data/comments.json'
    model = models.Comment
