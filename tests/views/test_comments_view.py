"""Test comments view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestCommentView(BaseTestView):
    """Test CommentService view."""

    base_path = '/comments'
    dependencies = [
        (models.Project, 'data/projects.json'),
        (models.Job, 'data/jobs.json'),
        (models.Asset, 'data/assets.json')
    ]
    file_path = 'data/comments.json'
    model = models.Comment
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'content': 'new message content',
        'author_id': '18d0e257-14d6-4e33-b873-fb506fffb42e',
        'entity_id': '039ff0b8-9504-4b10-865b-c2b67868b233'
    }
