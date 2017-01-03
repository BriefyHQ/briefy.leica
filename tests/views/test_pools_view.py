"""Test job pools view."""
from briefy.leica import models
from conftest import BaseVersionedTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestPoolOrderView(BaseVersionedTestView):
    """Test JobPoolService view."""

    base_path = '/pools'
    dependencies = [
    ]
    ignore_validation_fields = [
        'state_history', 'state'
    ]
    file_path = 'data/job_pools.json'
    model = models.JobPool
    initial_wf_state = 'created'
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'title': 'New JobPool title',
        'description': 'New Job Pool description'
    }
