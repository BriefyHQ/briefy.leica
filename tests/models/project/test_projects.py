"""Test Project database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestProjectModel(BaseModelTest):
    """Test Project."""

    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.InternalUserProfile, 'data/internal_profiles.json'),
    ]
    file_path = 'data/projects.json'
    model = models.Project

    def test_add_order_roles(self, instance_obj):
        """Set roles allowed to add orders/leads to the project."""
        instance_obj.add_order_roles = ['g:briefy_pm', 'g:briefy_support']

        assert 'g:briefy_pm' in instance_obj.add_order_roles
        assert 'g:briefy_support' in instance_obj.add_order_roles

    def test_add_order_roles_fails_on_non_existing_group(self, instance_obj):
        """Set add_order_roles will fail if group does not exist."""
        from briefy.ws.errors import ValidationError

        with pytest.raises(ValidationError) as exc:
            instance_obj.add_order_roles = ['g:foobar', 'g:briefy_support']

        assert exc.value.message == 'Invalid role'

    def test_settings_getter(self, instance_obj):
        """Test settings of a project."""
        settings = instance_obj.settings

        assert hasattr(settings, 'dates')

        assert settings.dates.approval_window == 5
        assert settings.dates.availability_window == 7
        assert settings.dates.cancellation_window == 1

        assert hasattr(settings, 'delivery_config')
        assert hasattr(settings, 'tech_requirements')

        assert hasattr(settings, 'permissions')
        assert 'g:briefy_pm' in settings.permissions.add_order._dct

    def test_settings_setter(self, instance_obj):
        """Test settings of a project."""
        settings = instance_obj.settings
        settings.permissions.add_order = ['g:customers']

        instance_obj.settings = settings

        new_settings = instance_obj.settings
        assert hasattr(new_settings, 'permissions')
        assert 'g:customers' in new_settings.permissions.add_order._dct
        assert 'g:briefy_support' not in new_settings.permissions.add_order._dct

    def test_leadorder_confirmation_fields(self, instance_obj):
        """Test leadorder_confirmation_fields of a project."""
        fields = instance_obj.leadorder_confirmation_fields

        assert fields == ['availability']

        instance_obj.leadorder_confirmation_fields = []

        fields = instance_obj.leadorder_confirmation_fields

        assert fields == []
