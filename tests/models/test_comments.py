"""Test Comment database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestCommentModel(BaseModelTest):
    """Test Comment."""

    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Job, 'data/jobs.json'),
        (models.Asset, 'data/assets.json'),
    ]
    file_path = 'data/comments.json'
    model = models.Comment
