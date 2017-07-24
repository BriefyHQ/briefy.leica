"""Test Professional database model."""
from briefy.leica import models
from conftest import BaseModelTest
from unittest.mock import patch

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestProfessionalModel(BaseModelTest):
    """Test Professional."""

    dependencies = [
        (models.Pool, 'data/jpools.json'),
    ]
    file_path = 'data/professionals.json'
    model = models.Professional

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

    def test_add_pool_to_professional(self, instance_obj):
        """Add job pools to the professional."""
        pools = models.Pool.query().all()
        assert len(pools) == 3
        assert len(instance_obj.pools) == 0

        for item in pools:
            instance_obj.pools.append(item)
            assert instance_obj in item.professionals
            assert len(item.professionals) == 1

        assert len(instance_obj.pools) == 3

    @pytest.mark.parametrize('origin_state', ['pending'])
    @pytest.mark.parametrize('role_name', ['qa', 'scout'])
    def test_workflow_approve(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test Professional workflow approve transition."""
        obj, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        with patch('briefy.leica.utils.user.get_user', return_value=None):
            wf.approve()
        session.flush()
        assert obj.initial_password is not None
        assert obj.initial_password == obj.to_dict()['initial_password']
        assert obj.state == 'validation'
        assert obj.state_history[-1]['transition'] == 'approve'

    @pytest.mark.parametrize('origin_state', ['pending'])
    @pytest.mark.parametrize('role_name', ['qa', 'scout'])
    def test_workflow_reject_quality(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test Professional workflow reject transition."""
        obj, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.reject()
        session.flush()
        assert obj.state == 'rejected'
        assert obj.state_history[-1]['transition'] == 'reject'

    @pytest.mark.parametrize('origin_state', ['validation'])
    @pytest.mark.parametrize('role_name', ['finance'])
    def test_workflow_validate(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test Professional workflow validate transition."""
        obj, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.validate()
        session.flush()
        assert obj.state == 'trial'
        assert obj.state_history[-1]['transition'] == 'validate'

    @pytest.mark.parametrize('origin_state', ['validation'])
    @pytest.mark.parametrize('role_name', ['finance'])
    def test_workflow_reject_from_validation(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test Professional workflow validate transition."""
        obj, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.reject()
        session.flush()
        assert obj.state == 'rejected'
        assert obj.state_history[-1]['transition'] == 'reject'

    @pytest.mark.parametrize('origin_state', ['trial', 'inactive'])
    @pytest.mark.parametrize('role_name', ['system', 'pm', 'qa', 'scout'])
    def test_workflow_activate(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test Professional workflow activate transition."""
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

    @pytest.mark.parametrize('origin_state', ['active', 'trial'])
    @pytest.mark.parametrize('role_name', ['system', 'pm', 'qa', 'scout'])
    def test_workflow_inactivate(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test Professional workflow inactivate transition."""
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

    @pytest.mark.parametrize(
        'origin_state',
        ['created', 'pending', 'validation', 'trial', 'rejected', 'active', 'inactive']
    )
    @pytest.mark.parametrize('role_name', ['scout', 'support'])
    def test_workflow_delete(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test Professional workflow delete transition."""
        obj, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.delete()
        session.flush()
        assert obj.state == 'deleted'
        assert obj.state_history[-1]['transition'] == 'delete'

    @pytest.mark.parametrize('origin_state', ['active', 'trial'])
    @pytest.mark.parametrize('role_name', ['system', 'pm', 'scout'])
    def test_workflow_assign(
        self, web_request, session, obj_payload, roles, role_name, origin_state
    ):
        """Test Professional workflow assign transition.

        In here we create new professionals and new pools to avoid a test issue with
        SQLAlchemy Continuum and the transaction per class fixture being used on this test.
        """
        from uuid import uuid4

        obj_payload['id'] = uuid4()
        obj_payload['email'] = str(obj_payload['id'])[6] + obj_payload['email']
        models.Professional.create(obj_payload)
        pool_id = uuid4()
        pool_payload = dict(
            id=pool_id,
            title='Pool fake',
            country='br'
        )
        models.Pool.create(pool_payload)
        instance_obj = models.Professional.get(obj_payload['id'])

        obj, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        wf.assign(fields={'pools_ids': [pool_id, ]})
        assert obj.state == origin_state
        assert obj.state_history[-1]['transition'] == 'assign'
