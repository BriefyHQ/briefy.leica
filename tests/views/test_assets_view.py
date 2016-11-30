"""Test assets view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest
import transaction


@pytest.mark.usefixtures('create_dependencies')
class TestAssetView(BaseTestView):
    """Test AssetService view."""

    base_path = '/jobs/c04dc102-7d3b-4574-a261-4bf72db571db/assets'
    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Job, 'data/jobs.json')
    ]
    file_path = 'data/images.json'
    model = models.Image
    initial_wf_state = 'pending'
    # TODO: author_id and uploaded_by should be validated
    ignore_validation_fields = ['state_history', 'state', 'updated_at', 'job',
                                'raw_metadata', 'uploaded_by', 'professional']
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
        # This id is from an asset in a distinct job
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
        # This id is from an asset in a distinct job
        obj_id = '740323b0-f97f-4c5a-b99a-71663e807051'

        # Conflicting project_id
        job_id = '67cbcef9-1354-415a-a1ff-498444647bdd'
        # Filter by object id
        params = {
            'id': obj_id,
            'job_id': job_id
        }
        request = app.get('{base}'.format(base=self.base_path),
                          params,
                          headers=self.headers, status=400)
        result = request.json

        assert result['status'] == 'error'
        assert 'Unknown filter field' in result['errors'][0]['description']
        assert 'job_id' in result['errors'][0]['name']

    def test_workflow(self):
        pass

    def test_versions_get_item(self, app, obj_payload):
        """Test get a item."""
        payload = obj_payload
        obj_id = payload['id']
        # Get original version
        request = app.get(
            '{base}/{id}/versions/0'.format(
                base=self.base_path, id=obj_id
            ),
            headers=self.headers,
            status=200
        )
        result = request.json
        db_obj = self.model.query().get(obj_id)
        assert db_obj.title != result['title']
        assert db_obj.versions[0].title == result['title']

    def test_versions_get_item_wrong_id(self, app, obj_payload):
        """Test get a item passing the wrong id."""
        payload = obj_payload
        obj_id = payload['id']
        # Get version 42 (does not exist here)
        request = app.get(
            '{base}/{id}/versions/42'.format(
                base=self.base_path, id=obj_id
            ),
            headers=self.headers,
            status=404
        )
        result = request.json
        assert 'Image with version: 42 not found' in result['message']

    def test_versions_get_collection(self, app, obj_payload):
        """Test get list of versions of an item."""
        payload = obj_payload
        obj_id = payload['id']
        request = app.get(
            '{base}/{id}/versions'.format(
                base=self.base_path, id=obj_id
            ),
            headers=self.headers,
            status=200
        )
        result = request.json
        assert 'versions' in result
        assert 'total' in result
        assert result['total'] == len(result['versions'])

        assert 'id' in result['versions'][0]
        assert 'updated_at' in result['versions'][0]
        assert 'id' in result['versions'][1]
        assert 'updated_at' in result['versions'][1]

        assert result['versions'][1]['id'] > result['versions'][0]['id']
        assert result['versions'][1]['updated_at'] > result['versions'][0]['updated_at']

    def test_machine_validation_invalidating(self, session, obj_payload, app):
        """Test creation of a new asset ending on edit state."""
        from briefy.leica.models import Job

        payload = obj_payload
        payload['id'] = '560a6697-11d2-4fe9-9757-a279c126b6bf'
        with transaction.manager:
            job = Job.get(payload['job_id'])
            project = job.project
            project.tech_requirements = {
                'dimensions': {'value': '800x600', 'operator': 'eq'},
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
