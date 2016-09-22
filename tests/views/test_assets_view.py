"""Test assets view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestAssetView(BaseTestView):
    """Test AssetService view."""

    base_path = '/jobs/c04dc102-7d3b-4574-a261-4bf72db571db/assets'
    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Job, 'data/jobs.json')
    ]
    file_path = 'data/assets.json'
    model = models.Asset
    initial_wf_state = 'pending'
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'title': 'New Image',
        'owner': 'New Owner',
        'author_id': 'd39c07c6-7955-489a-afce-483dfc7c9c5b'
    }

    def test_get_with_filters(self, app, obj_payload):
        """Test get a collection of items, filtered."""
        payload = obj_payload
        obj_id = payload['id']
        # Filter by object id
        params = {
            'id': obj_id
        }
        request = app.get('{base}'.format(base=self.base_path),
                          params,
                          headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == 1
        assert result['data'][0]['id'] == obj_id

    def test_get_filtering_state(self, app, obj_payload):
        """Test get a collection of items, filtered by state."""
        # Filter by state created
        params = {
            'state': 'created'
        }
        request = app.get('{base}'.format(base=self.base_path),
                          params,
                          headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == 1
        assert result['data'][0]['id'] == '7caa7704-7558-47f6-a00f-f3e18bbc06b6'
        assert result['data'][0]['state'] == 'created'

    def test_get_with_filters_with_wrong_id(self, app, obj_payload):
        """Test get a collection, filtering by the wrong id."""
        # This id is from an asset in a distinct job
        obj_id = '740323b0-f97f-4c5a-b99a-71663e807051'
        # Filter by object id
        params = {
            'id': obj_id
        }
        request = app.get('{base}'.format(base=self.base_path),
                          params,
                          headers=self.headers, status=200)
        result = request.json

        assert result['total'] == 0
        assert len(result['data']) == 0

    def test_get_with_filters_with_wrong_id_wrong_filter(self, app, obj_payload):
        """Test get a collection, filtering by the wrong id."""
        # This id is from an asset in a distinct job
        obj_id = '740323b0-f97f-4c5a-b99a-71663e807051'

        # Conflicting project_id
        job_id = '67cbcef9-1354-415a-a1ff-498444647bdd'
        # Filter by object id
        params = {
            'id': obj_id,
            'job_id': job_id
        }
        request = app.get('{base}'.format(base=self.base_path),
                          params,
                          headers=self.headers, status=400)
        result = request.json

        assert result['status'] == 'error'
        assert 'Unknown filter field' in result['errors'][0]['description']
        assert 'job_id' in result['errors'][0]['name']

    def test_workflow(self):
        pass
