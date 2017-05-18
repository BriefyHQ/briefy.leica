"""Test Professionals comments view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestProfessionalComments(BaseTestView):
    """Test Comments for a Professional."""

    base_path = '/professionals/23d94a43-3947-42fc-958c-09245ecca5f2/comments'
    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]
    file_path = 'data/comments_professional.json'
    model = models.Comment
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    ignore_validation_fields = ['entity', 'state', 'state_history']
    payload_position = 0
    update_map = {
        'content': 'new message content',
        'author_id': '18d0e257-14d6-4e33-b873-fb506fffb42e',
        'entity_id': '23d94a43-3947-42fc-958c-09245ecca5f2'
    }
