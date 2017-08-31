"""Test customer user profiles view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


LISTING_FILTERS_PAYLOADS = [
    ({'ilike_company_name': 'Other',
      'ilike_email': 'maike@lieferheld.de'}, 1),
    ({'gender': 'm',
      'ilike_title': 'Maike'}, 1),
    ({'ilike_title': 'Bork',
      'ilike_email': 'maike@lieferheld.de'}, 1),
]


@pytest.mark.usefixtures('create_dependencies')
class TestCustomerUserProfilesView(BaseTestView):
    """Test CustomerUserProfiles view."""

    base_path = '/profiles/customer'
    dependencies = []
    file_path = 'data/customer_profiles.json'
    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.CustomerUserProfile, 'data/customer_profiles.json'),
    ]
    model = models.CustomerUserProfile
    initial_wf_state = 'active'
    serialize_attrs = ['path', '_roles', '_actors', 'mobile', 'customers', 'projects']
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'company_name': 'Other',
        'internal': False,
        'partners': False,
        'customer_roles': ['customer_manager'],
        'project_customer_pm': [],
        'project_customer_qa': [],
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
