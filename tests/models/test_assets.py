"""Test Asset database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestAssetModel(BaseModelTest):
    """Test Asset."""

    dependencies = [
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

    def test_workflow(self):
        return True
