"""Test CustomerUserProfile database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest
import transaction


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

    def test_remove_add_project(self, instance_obj):
        """Remove and add back one project from customer user."""
        user = instance_obj
        user_id = user.id
        transaction.commit()

        user = models.CustomerUserProfile.get(user_id)
        ids = list(user.project_ids)
        removed = ids.pop()
        user.project_roles = ids
        transaction.commit()

        user = models.CustomerUserProfile.get(user_id)
        assert removed not in user.project_ids
        ids = list(user.project_ids)
        ids.append(removed)
        user.project_roles = ids
        transaction.commit()

        user = models.CustomerUserProfile.get(user_id)
        assert removed in user.project_ids
