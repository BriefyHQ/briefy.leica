"""Test customer user profiles view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestCustomerUserProfileslView(BaseTestView):
    """Test CustomerUserProfiles view."""

    base_path = '/profiles/customer'
    dependencies = []
    file_path = 'data/customer_profiles.json'
    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
    ]
    model = models.CustomerUserProfile
    initial_wf_state = 'active'
    ignore_validation_fields = [
        'state_history',
        'state',
        'customer_roles',
        'project_roles',
        'customers',
        'projects',
    ]
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'company_name': 'Outro nome',
        'internal': False,
        'partners': False,
        'gender': 'm',
    }
