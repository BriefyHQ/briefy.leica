"""Test InternalUserProfile database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestInternalUserProfileModel(BaseModelTest):
    """Test Internal user profiles."""

    file_path = 'data/internal_profiles.json'
    model = models.InternalUserProfile
    initial_wf_state = 'active'
