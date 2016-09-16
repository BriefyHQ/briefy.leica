"""Test projects view."""
from briefy.leica import models
from conftest import BaseTestView


class TestProjectView(BaseTestView):
    """Test ProjecService view."""

    base_path = '/projects'
    file_path = 'data/projects.json'
    model = models.Project
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'briefing': 'The briefy',
        'currency_set_price': 'USD',
        'abstract': 'The abstract',
        'company_id': '66e07fc8-f237-4bab-a883-14234b258513',
        'name': 'Other Name',
        'set_price': 200,
    }
