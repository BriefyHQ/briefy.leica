"""Test jobs view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest
import transaction


@pytest.mark.usefixtures('create_dependencies')
class TestJobView(BaseTestView):
    """Test JobService view."""

    base_path = '/jobs'
    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json')
    ]
    ignore_validation_fields = ['state_history', 'state', 'project', 'customer', 'updated_at']
    file_path = 'data/jobs.json'
    model = models.Job
    initial_wf_state = 'pending'
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'title': 'Job Title',
        'job_id': '10',
        'project_id': '36d359f0-8e92-41bb-8d1c-fedfd60e7046'
    }

    def test_workflow(self, app, session, instance_obj):
        """Test workflow endpoints."""
        obj_id = instance_obj.id
        payload = {
            'owner': 'Professional Name',
            'id': '264b3e66-c327-4bbd-9cc7-271716fce178',
            'author_id': '23d94a43-3947-42fc-958c-09245ecca5f2',
            'uploaded_by': '23d94a43-3947-42fc-958c-09245ecca5f2',
            'description': '',
            'updated_at': '2016-09-18T18:55:20.696061+00:00',
            'filename': '2345.jpg',
            'source_path': 'source/files/jobs/2345.jpg',
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
            'job_id': 'c04dc102-7d3b-4574-a261-4bf72db571db',
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
        assert 'workaround_qa' in result['transitions']

        # Transition to in_qa
        payload = {
            'transition': 'workaround_qa',
            'message': 'In qa'
        }
        request = app.post_json(
            endpoint,
            payload,
            headers=self.headers,
            status=200
        )
        result = request.json
        assert result['status'] is True

        # Transition to approved will raise an error because we do not have the
        # required number of assets
        payload = {
            'transition': 'approve',
            'message': 'Good set'
        }
        request = app.post_json(
            endpoint,
            payload,
            headers=self.headers,
            status=400
        )
        result = request.json
        assert result['status'] == 'error'

        # Change the number of required photos
        with transaction.manager:
            job = models.Job.get(obj_id)
            job.number_of_photos = 1
            session.add(job)
            session.flush()

        request = app.post_json(
            endpoint,
            payload,
            headers=self.headers,
            status=200
        )
        job = models.Job.get(obj_id)
        result = request.json
        assert result['status'] is True
        assert result['message'] == 'Transition executed: approve'
        assert job.assets[0].state == 'approved'
