"""Test comments view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestAssetComment(BaseTestView):
    """Test Comments for an Asset."""

    base_path = (
        '/jobs/cf326cc7/assets/bf721f30-79ce-4bc7-9887-79b6c53c681d/comments'
    )
    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Job, 'data/jobs.json'),
        (models.Asset, 'data/assets.json')
    ]
    file_path = 'data/comments.json'
    model = models.Comment
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''

    payload_position = 5

    update_map = {
        'content': 'new message content',
        'author_id': '18d0e257-14d6-4e33-b873-fb506fffb42e',
        'entity_id': '28bd9151-222a-4076-abe0-5867bf22f18d'
    }
