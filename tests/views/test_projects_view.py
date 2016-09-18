"""Test projects view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestProjectView(BaseTestView):
    """Test ProjectService view."""

    base_path = '/projects'
    dependencies = [
        (models.Customer, 'data/customers.json')
    ]
    file_path = 'data/projects.json'
    model = models.Project
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'description': 'The briefy',
        'customer_id': 'c2034c1b-0a40-4b84-9ace-54b958f64ed4',
        'title': 'Other Name'
    }
