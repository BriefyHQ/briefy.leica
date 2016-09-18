"""Test jobs view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestJobView(BaseTestView):
    """Test JobService view."""

    base_path = '/jobs'
    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json')
    ]
    file_path = 'data/jobs.json'
    model = models.Job
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'title': 'Job Title',
        'job_id': '10',
        'project_id': '36d359f0-8e92-41bb-8d1c-fedfd60e7046'
    }
