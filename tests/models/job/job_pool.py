"""Test JobPool database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestJobPoolModel(BaseModelTest):
    """Test JobPool."""

    dependencies = [
    ]
    file_path = 'data/job_pools.json'
    model = models.JobPool
    initial_wf_state = 'created'
    number_of_wf_transtions = 1
