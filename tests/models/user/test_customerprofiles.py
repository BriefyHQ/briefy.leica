"""Test CustomerUserProfile database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestCustomerUserProfileModel(BaseModelTest):
    """Test Customer user profiles."""

    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
    ]
    file_path = 'data/customer_profiles.json'
    model = models.CustomerUserProfile
    initial_wf_state = 'active'
