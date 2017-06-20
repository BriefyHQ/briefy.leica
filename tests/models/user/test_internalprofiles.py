"""Test BriefyUserProfile database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestBriefyUserProfileModel(BaseModelTest):
    """Test Internal user profiles."""

    dependencies = []
    file_path = 'data/internal_profiles.json'
    model = models.BriefyUserProfile
    initial_wf_state = 'active'

    @staticmethod
    def prepare_obj_wf(obj, web_request, role=None, state=None):
        """Prepare the instance obj to transition test."""
        if state:
            obj.state = state
        obj.request = web_request
        wf = obj.workflow
        if role:
            web_request.user = role
            wf.context = role
        return obj, wf, web_request

    @pytest.mark.parametrize('origin_state', ['created', 'inactive'])
    @pytest.mark.parametrize('role_name', ['support', 'system'])
    def test_workflow_activate(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test Customer User Profile workflow activate transition."""
        obj, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.activate()
        session.flush()
        assert obj.state == 'active'
        assert obj.state_history[-1]['transition'] == 'activate'

    @pytest.mark.parametrize('origin_state', ['active'])
    @pytest.mark.parametrize('role_name', ['support', 'system'])
    def test_workflow_inactivate(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test Customer User Profile workflow inactivate transition."""
        obj, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.inactivate()
        session.flush()
        assert obj.state == 'inactive'
        assert obj.state_history[-1]['transition'] == 'inactivate'
