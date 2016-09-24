"""Test Asset database model."""
from briefy.leica import models
from conftest import BaseModelTest
from sqlalchemy_continuum.utils import count_versions

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

    def test_workflow(self):
        return True
