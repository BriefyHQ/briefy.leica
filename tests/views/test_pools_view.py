"""Test Pools view."""
from briefy.leica import models
from conftest import BaseVersionedTestView

import pytest


LISTING_FILTERS_PAYLOADS = [
    ({'ilike_title': 'New',
      'country': 'ID',
      'ilike_description': 'pool'}, 1),
    ({'ilike_title': 'Phuket',
      'country': 'TH',
      'ilike_description': 'pool'}, 1),
    ({'ilike_title': 'Bangkok',
      'country': 'TH',
      'ilike_description': 'pool'}, 1),
]


@pytest.mark.usefixtures('create_dependencies')
class TestPoolOrderView(BaseVersionedTestView):
    """Test PoolService view."""

    base_path = '/pools'
    dependencies = [
        (models.Pool, 'data/jpools.json'),
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

    @pytest.mark.parametrize('filter_payload, total', LISTING_FILTERS_PAYLOADS)
    def test_collection_get_with_filters(self, app, filter_payload, total):
        """Test collection_get endpoint with special filters."""
        base_path = self.get_base_path_with_query_str(filter_payload)
        request = app.get(base_path, headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == len(result['data']) == total
