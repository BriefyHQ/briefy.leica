"""Test internal user profiles view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


LISTING_FILTERS_PAYLOADS = [
    ({'ilike_title': 'Mo Hamed',
      'ilike_email': 'mo@briefy.co'}, 1),
    ({'ilike_title': 'Grace',
      'ilike_email': 'grace@briefy.co'}, 1),
    ({'ilike_title': 'Franco',
      'ilike_email': 'franco@briefy.co'}, 1),
    ({'ilike_title': 'Ansgar',
      'ilike_email': 'ansgar@briefy.co'}, 1),
]


@pytest.mark.usefixtures('create_dependencies')
class TestCustomerUserProfileslView(BaseTestView):
    """Test InternalUserProfiles view."""

    base_path = '/profiles/internal'
    dependencies = [
        (models.InternalUserProfile, 'data/internal_profiles.json'),
    ]
    file_path = 'data/internal_profiles.json'
    model = models.InternalUserProfile
    initial_wf_state = 'active'
    serialize_attrs = ['path', '_roles', '_actors', 'mobile']
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'company_name': 'Other',
        'internal': False,
        'partners': False,
        'gender': 'm',
        'mobile': '+49 176 28697522'
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
