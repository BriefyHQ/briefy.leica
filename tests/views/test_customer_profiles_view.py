"""Test customer user profiles view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestCustomerUserProfilesView(BaseTestView):
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
