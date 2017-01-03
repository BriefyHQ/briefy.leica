"""Test professionals view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestProfessionalView(BaseTestView):
    """Test ProfessionalService view."""

    base_path = '/professionals'
    dependencies = []
    file_path = 'data/professionals.json'
    model = models.Professional

    ignore_validation_fields = ['state_history', 'state']

    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'description': 'Just another photographer',
    }
