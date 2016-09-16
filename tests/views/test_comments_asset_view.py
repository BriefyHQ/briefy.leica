"""Test comments view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestAssetComment(BaseTestView):
    """Test Comments for an Asset."""

    base_path = (
        '/jobs/cf326cc7/assets/073355e3-0988-458e-9216-e882154a9699/comments'
    )
    dependencies = [
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
        'entity_id': '073355e3-0988-458e-9216-e882154a9699'
    }
