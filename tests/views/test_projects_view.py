"""Test projects view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestProjectView(BaseTestView):
    """Test ProjectService view."""

    base_path = '/projects'
    dependencies = [
        (models.Customer, 'data/customers.json')
    ]
    file_path = 'data/projects.json'
    model = models.Project
    initial_wf_state = 'ongoing'
    ignore_validation_fields = [
        'state_history', 'state', 'customer', 'updated_at',
        'qa_manager', 'project_manager', 'scout_manager', 'versions', 'orders'
    ]

    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'description': 'The briefy',
        'customer_id': 'c2034c1b-0a40-4b84-9ace-54b958f64ed4',
        'title': 'Other Name'
    }
    def test_put_invalid_asset_tyoe(self, app, obj_payload):
        """Asset type should match one of the possible values."""
        payload = obj_payload
        obj_id = payload['id']
        payload['asset_types'] = ['Foobar']
        request = app.put_json('{base}/{id}'.format(base=self.base_path, id=obj_id),
                               payload, headers=self.headers, status=400)
        result = request.json
        error = result['errors'][0]
        assert result['status'] == 'error'
        assert error['name'] == 'asset_types'
        assert error['location'] == 'body'
        assert 'Invalid type of asset' in error['description']
