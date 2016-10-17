"""Test Asset database model."""
from briefy.common.types import BaseUser
from briefy.leica import models
from conftest import BaseModelTest
from conftest import mock_rolleiflex
from conftest import mock_thumbor
from sqlalchemy_continuum.utils import count_versions

import httmock
import pytest
import transaction


@pytest.mark.usefixtures('create_dependencies')
class TestAssetModel(BaseModelTest):
    """Test Asset."""

    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Job, 'data/jobs.json')
    ]

    file_path = 'data/assets.json'
    model = models.Asset
    number_of_wf_transtions = 1

    def test_obj_to_dict_serializes_image(self, instance_obj):
        """Test if the to_dict serializes image property."""
        serialized = instance_obj.to_dict()
        assert 'image' in serialized
        assert isinstance(serialized['image'], dict)

        assert 'download' in serialized['image']
        assert 'width' in serialized['image']
        assert 'height' in serialized['image']

        assert isinstance(serialized['image']['scales'], dict)
        assert 'original' in serialized['image']['scales']

    def test_obj_to_dict_serializes_metadata(self, instance_obj):
        """Test if the to_dict serializes metadata_ property."""
        serialized = instance_obj.to_dict()
        assert 'metadata' in serialized
        assert isinstance(serialized['metadata'], dict)

        assert 'aperture' in serialized['metadata']
        assert 'iso' in serialized['metadata']
        assert 'shutter' in serialized['metadata']

    def test_asset_is_valid(self, instance_obj):
        """Test if the asset is valid."""
        asset = instance_obj
        job = asset.job
        project = job.project
        project.tech_requirements = {
            'dimensions': {'value': '5760x3840', 'operator': 'eq'},
        }

        assert asset.is_valid is True

        project.tech_requirements = {
            'dpi': {'value': '300', 'operator': 'eq'},
            'dimensions': {'value': '5760x3840', 'operator': 'eq'},
        }

        assert asset.is_valid is False

    def test_obj_versioning(self, session, obj_payload):
        """Test object versioning."""
        # We will create a new object, so change the id from the payload
        payload = obj_payload
        obj_id = 'fc1ceab8-6c2a-4b19-8f96-cf8c6e56ca88'
        payload['id'] = obj_id
        # Create the object using a new transaction
        with transaction.manager:
            asset = models.Asset(**payload)
            session.add(asset)
            session.flush()

        obj = models.Asset.get(obj_id)
        obj_source_path = obj.source_path

        assert count_versions(obj) == 1
        assert obj.version == 0

        # now we change the source_path using a new transaction
        with transaction.manager:
            obj.source_path = 'foo_bar.jpg'
            session.add(obj)
            session.flush()

        obj = models.Asset.get(obj_id)
        assert obj.version == 1
        assert count_versions(obj) == 2
        assert obj.source_path == 'foo_bar.jpg'
        assert obj.versions[0].source_path != 'foo_bar.jpg'
        assert obj.versions[0].source_path == obj_source_path

    def test_workflow(self, instance_obj, roles):
        """Test workflow for this model."""
        from briefy.common.workflow.exceptions import WorkflowTransitionException

        asset = instance_obj
        job = asset.job
        job.state = 'awaiting_assets'

        wf = asset.workflow

        with httmock.HTTMock(mock_rolleiflex):
            # Object starts as created
            assert asset.state == 'created'

            # Professional can move it to validation
            wf.context = roles['professional']
            assert 'submit' in wf.transitions
            # System as well
            wf.context = roles['system']
            assert 'submit' in wf.transitions
            # QA as well
            wf.context = roles['qa']
            assert 'submit' in wf.transitions

            # Professional moves it to validation
            wf.context = roles['professional']
            with httmock.HTTMock(mock_thumbor):
                wf.submit()

            assert asset.state == 'validation'
            # And now Professional is not able to move the object anymore
            assert len(wf.transitions) == 0

            # System will invalidate the submission
            wf.context = roles['system']
            wf.invalidate()
            assert asset.state == 'edit'

            # Professional now can edit the job and submit it again
            wf.context = roles['professional']
            assert len(wf.transitions) == 2
            assert 'submit' in wf.transitions
            with httmock.HTTMock(mock_thumbor):
                wf.submit()
            assert asset.state == 'validation'

            # System will validate the submission
            wf.context = roles['system']
            wf.validate()
            assert asset.state == 'pending'

            # QA could transition to 5 distinct states
            wf.context = roles['qa']
            assert len(wf.transitions) == 5
            assert 'request_edit' in wf.transitions
            assert 'discard' in wf.transitions
            assert 'process' in wf.transitions
            assert 'reserve' in wf.transitions
            assert 'approve' in wf.transitions

            # QA request an edit
            wf.request_edit()
            assert asset.state == 'edit'
            # Professional re-submits it and validation works
            wf.context = roles['professional']
            wf.submit()
            wf.context = roles['system']
            wf.validate()

            # QA will discard it and get it back
            wf.context = roles['qa']
            wf.discard()
            wf.retract()

            # QA will processe it and get it back
            wf.process()
            wf.retract()

            # QA will reserve it and get it back
            wf.reserve()
            wf.retract()

            # QA will approve it
            wf.approve()
            wf.state == 'approved'

            # Customer can reject it
            wf.context = roles['customer']
            assert len(wf.transitions) == 1
            assert 'reject' in wf.transitions

            # System can mark it as delivered
            wf.context = roles['system']
            assert len(wf.transitions) == 1
            assert 'deliver' in wf.transitions
            wf.deliver()
