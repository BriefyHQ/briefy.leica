"""Test Professional database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestProfessionalModel(BaseModelTest):
    """Test Professional."""

    dependencies = [
        (models.Pool, 'data/jpools.json'),
    ]
    file_path = 'data/professionals.json'
    model = models.Professional

    def test_add_pool_to_professional(self, instance_obj, session):
        """Add job pools to the professional."""
        pools = models.Pool.query().all()
        assert len(pools) == 3
        assert len(instance_obj.pools) == 0

        for item in pools:
            instance_obj.pools.append(item)
            assert instance_obj.id == item.professionals[0].id
            assert len(item.professionals) == 1

        session.flush()
        assert len(instance_obj.pools) == 3
