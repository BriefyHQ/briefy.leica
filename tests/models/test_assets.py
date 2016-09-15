"""Test Asset database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestAssetModel(BaseModelTest):
    """Test Asset."""

    dependencies = [
        (models.Project, 'data/projects.json'),
        (models.Job, 'data/jobs.json')
    ]

    file_path = 'data/assets.json'
    model = models.Asset
    number_of_wf_transtions = 1
