"""Test job order comments view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestJobOrderComments(BaseTestView):
    """Test Comments for a Job order."""

    base_path = '/orders/011418fa-f450-4deb-b6ea-7f8e103a66d1/comments'
    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.JobOrder, 'data/job_orders.json'),
        (models.JobAssignment, 'data/jobs.json'),
        (models.Image, 'data/images.json')
    ]
    file_path = 'data/comments.json'
    model = models.Comment
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    payload_position = 10
    update_map = {
        'content': 'new message content',
        'author_id': '18d0e257-14d6-4e33-b873-fb506fffb42e',
        'entity_id': '3a21070d-6c77-4239-91ab-7ba4e86dc909'
    }
