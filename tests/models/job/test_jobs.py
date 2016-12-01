"""Test Jobs database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestJobModel(BaseModelTest):
    """Test Job."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json')
    ]
    file_path = 'data/jobs.json'
    model = models.Job

    def test_workflow(self, instance_obj, roles):
        """Test workflow for this model."""
        from briefy.common.workflow.exceptions import WorkflowTransitionException

        job = instance_obj
        wf = job.workflow

        # Object starts as created
        assert job.state == 'created'

        # Customer can move it to validation
        wf.context = roles['customer']
        assert 'submit' in wf.transitions
        # System as well
        wf.context = roles['system']
        assert 'submit' in wf.transitions
        # PM cannot
        wf.context = roles['pm']
        assert 'submit' not in wf.transitions

        # Customer moves it to validation
        wf.context = roles['customer']
        wf.submit()

        # Validation happened already
        assert job.state == 'pending'

        # Customer or PM can publish this job to job pool
        wf.context = roles['pm']
        assert 'publish' in wf.transitions

        wf.context = roles['customer']
        assert 'publish' in wf.transitions

        # Customer can also cancel the job
        assert 'cancel' in wf.transitions

        # Scout can assign it to a professional
        wf.context = roles['scout']
        assert 'assign' in wf.transitions
        wf.assign()
        assert job.state == 'assigned'

        # Customer can still cancel the job
        wf.context = roles['customer']
        assert 'cancel' in wf.transitions

        # Professional can schedule the job or report scheduling issues
        wf.context = roles['professional']
        assert 'schedule' in wf.transitions
        wf.scheduling_issues()
        # Job will still be assigned
        assert job.state == 'assigned'

        wf.schedule()
        assert job.state == 'scheduled'

        # Customer can still cancel the job
        wf.context = roles['customer']
        assert 'cancel' in wf.transitions

        # System is now able to move the job to awaiting for assets
        wf.context = roles['system']
        assert 'ready_for_upload' in wf.transitions
        wf.ready_for_upload()
        assert job.state == 'awaiting_assets'

        # Customer can not cancel this job anymore
        wf.context = roles['customer']
        assert 'cancel' not in wf.transitions

        # Professional can re-schedule this job
        wf.context = roles['professional']
        assert 'schedule' in wf.transitions

        # Professional can re-schedule this job or send it to qa
        wf.context = roles['professional']
        assert 'schedule' in wf.transitions
        assert 'upload' in wf.transitions
        wf.upload()

        # QA can reject or approve the job
        wf.context = roles['qa']
        assert 'approve' in wf.transitions
        assert 'reject' in wf.transitions
        # Trying to approve a job with the wrong number of assets with raise an exception
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.approve()

        assert 'Incorrect number of assets' in str(excinfo)
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.reject()
        assert 'Message is required' in str(excinfo)
        wf.reject(message='Missing 5 or 6 pictures')

        assert job.state == 'awaiting_assets'

        # Professional upload new assets and QA approves it
        wf.context = roles['professional']
        wf.upload()

        job.number_of_photos = 0
        wf.context = roles['qa']
        wf.approve()
        assert job.state == 'approved'
        assert 'retract_approval' in wf.transitions

        # System can execute a deliver transition
        # This triggers an event to be picked by briefy.courier
        wf.context = roles['system']
        assert 'deliver' in wf.transitions
        wf.deliver()
        assert job.state == 'approved'

        # System or PM can move job to completed
        wf.context = roles['system']
        assert 'complete' in wf.transitions

        wf.context = roles['pm']
        assert 'complete' in wf.transitions

        # Customer can approve or reject the job
        wf.context = roles['customer']
        assert 'complete' in wf.transitions
        assert 'refuse' in wf.transitions
        wf.refuse(message='Need a picture of the pool')

        assert job.state == 'refused'

        # PM could decide to move job to complete or send it back to QA
        wf.context = roles['pm']
        assert 'complete' in wf.transitions
        assert 'retract_approval' in wf.transitions

        # Customer could also move the job to completed from here
        wf.context = roles['customer']
        assert 'complete' in wf.transitions
        wf.complete()
        assert job.state == 'completed'

        # After completion, only the system can execute a transition to the job
        for role in ('customer', 'professional', 'pm', 'qa', 'scout'):
            wf.context = roles[role]
            assert len(wf.transitions) == 0
