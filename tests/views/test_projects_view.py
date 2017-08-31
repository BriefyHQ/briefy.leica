"""Test projects view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


LISTING_FILTERS_PAYLOADS = [
    ({'ilike_title': 'project'}, 4),
    ({'ilike_title': 'other'}, 1),
    ({'ilike_title': 'project',
      'ilike_customer.title': 'client'}, 4),
]


@pytest.mark.usefixtures('create_dependencies')
class TestProjectView(BaseTestView):
    """Test ProjectService view."""

    base_path = '/projects'
    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Pool, 'data/jpools.json'),
        (models.Project, 'data/projects.json')
    ]
    file_path = 'data/projects.json'
    model = models.Project
    initial_wf_state = 'ongoing'
    serialize_attrs = [
        'path', '_roles', '_actors', 'customer', 'orders', 'leadorders', 'pool'
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

    @pytest.mark.parametrize('filter_payload, total', LISTING_FILTERS_PAYLOADS)
    def test_collection_get_with_filters(self, app, filter_payload, total):
        """Test collection_get endpoint with special filters."""
        base_path = self.get_base_path_with_query_str(filter_payload)
        request = app.get(base_path, headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == len(result['data']) == total
