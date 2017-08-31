"""Test Pool database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestPoolModel(BaseModelTest):
    """Test Pool."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]
    file_path = 'data/jpools.json'
    model = models.Pool
    initial_wf_state = 'created'
    number_of_wf_transtions = 1

    def test_add_professional_to_pool(self, instance_obj, session):
        """Add professionals to the Pool."""
        professionals = models.Professional.query().all()
        assert len(professionals) == 3
        assert len(instance_obj.professionals) == 0

        for prof in professionals:
            instance_obj.professionals.append(prof)
            assert prof in instance_obj.professionals
            assert instance_obj in prof.pools

        assert len(instance_obj.professionals) == 3
