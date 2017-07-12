"""Test internal user profiles view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestCustomerUserProfileslView(BaseTestView):
    """Test InternalUserProfiles view."""

    base_path = '/profiles/internal'
    dependencies = []
    file_path = 'data/internal_profiles.json'
    model = models.InternalUserProfile
    initial_wf_state = 'active'
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'company_name': 'Other',
        'internal': False,
        'partners': False,
        'gender': 'm',
    }
