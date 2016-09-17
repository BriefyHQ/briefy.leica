"""Test jobs view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestJobView(BaseTestView):
    """Test JobService view."""

    base_path = '/jobs'
    dependencies = [
        (models.Project, 'data/projects.json')
    ]
    file_path = 'data/jobs.json'
    model = models.Job
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'title': 'Job Title',
        'internal_job_id': '10',
        'project_id': '5ae9e8bb-1954-414b-8e60-debfd9120edc'
    }
