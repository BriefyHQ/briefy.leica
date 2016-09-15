"""Test assets view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestAssetView(BaseTestView):
    """Test AssetService view."""

    base_path = '/assets'
    dependencies = [
        (models.Project, 'data/projects.json'),
        (models.Job, 'data/jobs.json')
    ]
    file_path = 'data/assets.json'
    model = models.Asset
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'title': 'New Image',
        'owner': 'New Owner',
        'author_id': 'd39c07c6-7955-489a-afce-483dfc7c9c5b',
        'job_id': '67cbcef9-1354-415a-a1ff-498444647bdd'
    }

