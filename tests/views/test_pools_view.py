"""Test Pools view."""
from briefy.leica import models
from conftest import BaseVersionedTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestPoolOrderView(BaseVersionedTestView):
    """Test PoolService view."""

    base_path = '/pools'
    dependencies = [
    ]
    ignore_validation_fields = [
        'state_history', 'state'
    ]
    file_path = 'data/jpools.json'
    model = models.Pool
    initial_wf_state = 'created'
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'title': 'New Pool title',
        'description': 'New Pool description'
    }
