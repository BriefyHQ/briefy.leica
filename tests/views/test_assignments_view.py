"""Test Assignments Service view."""
from briefy.leica import models
from conftest import BaseVersionedTestView

import pytest
import transaction


@pytest.mark.usefixtures('create_dependencies')
class TestAssignmentView(BaseVersionedTestView):
    """Test AssignmentService view."""

    base_path = '/assignments'
    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Order, 'data/orders.json'),
    ]
    # TODO: local role attributes are not in the colander schema and so ignored on add or update
    ignore_validation_fields = [
        'state_history', 'state', 'order', 'updated_at', 'customer', 'project', 'timezone',
        'qa_manager', 'project_manager', 'scout_manager', 'professional', 'location'
    ]
    file_path = 'data/assignments.json'
    model = models.Assignment
    initial_wf_state = 'pending'
    check_versions_field = 'payout_currency'
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'payable': False,
        'travel_expenses': 1000,
        'payout_currency': 'USD'
    }

    def test_workflow(self, app, session, instance_obj):
        """Test workflow endpoints."""
        obj_id = instance_obj.id
        payload = {
            'owner': 'Professional Name',
            'id': '264b3e66-c327-4bbd-9cc7-271716fce178',
            'professional_id': '23d94a43-3947-42fc-958c-09245ecca5f2',
            'uploaded_by': '23d94a43-3947-42fc-958c-09245ecca5f2',
            'description': '',
            'updated_at': '2016-09-18T18:55:20.696061+00:00',
            'filename': '2345.jpg',
            'source_path': 'source/files/assignments/2345.jpg',
            'created_at': '2016-09-18T18:55:20.696043+00:00',
            'state': 'pending',
            'width': 5760,
            'height': 3840,
            'content_type': 'image/jpeg',
            'state_history': [
                {
                    'actor': '',
                    'date': '2016-09-28T20:08:37.217221+00:00',
                    'from': 'created',
                    'message': 'Imported in this state from Knack database',
                    'to': 'validation',
                    'transition': 'submit'
                },
                {
                    'actor': '',
                    'date': '2016-09-28T20:08:37.217221+00:00',
                    'from': 'validation',
                    'message': 'Correct dimensions',
                    'to': 'pending',
                    'transition': 'validate'
                }
            ],
            'size': 4049867,
            'assignment_id': 'c04dc102-7d3b-4574-a261-4bf72db571db',
            'title': 'IMAGE01'
        }
        # Create the object using a new transaction
        with transaction.manager:
            asset = models.Asset(**payload)
            session.add(asset)
            session.flush()

        obj_id = instance_obj.id
        state = instance_obj.state

        assert state == 'pending'

        # Endpoints
        endpoint = '{base}/{id}/transitions'.format(
            base=self.base_path, id=obj_id
        )

        # List available transitions
        request = app.get(
            endpoint,
            headers=self.headers,
            status=200
        )
        result = request.json
        assert result['total'] == 4
        assert 'cancel' in result['transitions']
        assert 'publish' in result['transitions']
        assert 'assign' in result['transitions']
