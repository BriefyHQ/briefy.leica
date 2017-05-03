"""Test LeadOrder database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestLeadOrderModel(BaseModelTest):
    """Test LeadOrder."""

    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json')
    ]
    file_path = 'data/leadorders.json'
    model = models.LeadOrder
    initial_wf_state = 'new'
