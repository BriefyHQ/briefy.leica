"""Test assets view."""
from briefy.leica import models
from conftest import BaseVersionedTestView

import pytest
import transaction


@pytest.mark.usefixtures('create_dependencies')
class TestAssetView(BaseVersionedTestView):
    """Test AssetService view."""

    base_path = '/assignments/c04dc102-7d3b-4574-a261-4bf72db571db/assets'
    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Order, 'data/orders.json'),
        (models.Assignment, 'data/assignments.json')
    ]
    file_path = 'data/images.json'
    model = models.Image
    initial_wf_state = 'pending'
    # TODO: author_id and uploaded_by should be validated
    ignore_validation_fields = [
        'state_history', 'state', 'updated_at', 'assignment',
        'raw_metadata', 'uploaded_by', 'professional', 'professional_user',
    ]
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'title': 'New Image',
        'owner': 'New Owner',
        'source_path': 'path/to/foo/bar.jpg',
        'professional_id': 'd39c07c6-7955-489a-afce-483dfc7c9c5b'
    }

    def test_get_with_filters(self, app, obj_payload):
        """Test get a collection of items, filtered."""
        payload = obj_payload
        obj_id = payload['id']
        # Filter by object id
        params = {
            'id': obj_id
        }
        request = app.get('{base}'.format(base=self.base_path),
                          params,
                          headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == 1
        assert result['data'][0]['id'] == obj_id

    def test_get_filtering_state(self, app, obj_payload):
        """Test get a collection of items, filtered by state."""
        # Filter by state created
        params = {
            'state': 'pending'
        }
        request = app.get('{base}'.format(base=self.base_path),
                          params,
                          headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == 1
        assert result['data'][0]['id'] == '7caa7704-7558-47f6-a00f-f3e18bbc06b6'
        assert result['data'][0]['state'] == 'pending'

    def test_get_with_filters_with_wrong_id(self, app, obj_payload):
        """Test get a collection, filtering by the wrong id."""
        # This id is from an asset in a distinct assignment
        obj_id = '740323b0-f97f-4c5a-b99a-71663e807051'
        # Filter by object id
        params = {
            'id': obj_id
        }
        request = app.get('{base}'.format(base=self.base_path),
                          params,
                          headers=self.headers, status=200)
        result = request.json

        assert result['total'] == 0
        assert len(result['data']) == 0

    def test_get_with_filters_with_wrong_id_wrong_filter(self, app, obj_payload):
        """Test get a collection, filtering by the wrong id."""
        # This id is from an asset in a distinct assignment
        obj_id = '740323b0-f97f-4c5a-b99a-71663e807051'

        # Conflicting project_id
        assignment_id = '67cbcef9-1354-415a-a1ff-498444647bdd'
        # Filter by object id
        params = {
            'id': obj_id,
            'assignment_id': assignment_id
        }
        request = app.get('{base}'.format(base=self.base_path),
                          params,
                          headers=self.headers, status=400)
        result = request.json

        assert result['status'] == 'error'
        assert 'Unknown filter field' in result['errors'][0]['description']
        assert 'assignment_id' in result['errors'][0]['name']

    def test_workflow(self):
        pass

    def test_machine_validation_invalidating(self, session, obj_payload, app):
        """Test creation of a new asset ending on edit state."""
        from briefy.leica.models import Assignment

        payload = obj_payload
        payload['id'] = '560a6697-11d2-4fe9-9757-a279c126b6bf'
        with transaction.manager:
            assignment = Assignment.get(payload['assignment_id'])
            project = assignment.order.project
            project.tech_requirements = {
                'asset': {
                    'dimensions': {'value': '800x600', 'operator': 'eq'},
                }
            }
            session.add(project)
            session.flush()

        request = app.post_json(self.base_path, payload, headers=self.headers, status=200)

        assert 'application/json' == request.content_type

        db_obj = self.model.query().get(payload['id'])

        assert db_obj.state == 'edit'
        history = db_obj.state_history
        assert len(history) == 3
        assert history[2]['message'] == 'Dimensions check failed 5760 x 3840'
