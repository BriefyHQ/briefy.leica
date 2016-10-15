"""Test Jobs database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest

from briefy.common.types import BaseUser


@pytest.mark.usefixtures('create_dependencies')
class TestJobModel(BaseModelTest):
    """Test Job."""

    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json')
    ]
    file_path = 'data/jobs.json'
    model = models.Job

    def get_roles(self) -> dict:
        """Return a dict with users in distinct roles."""
        base = {
            'locale': 'en_GB',
            'fullname': '',
            'first_name': '',
            'email': '',
            'last_name': '',
            'groups': []
        }
        customer = base.copy()
        customer['groups'] = ['g:customers', ]
        professional = base.copy()
        professional['groups'] = ['g:professionals', ]
        system = base.copy()
        system['groups'] = ['g:system', ]
        qa = base.copy()
        qa['groups'] = ['g:briefy_qa', ]
        scout = base.copy()
        scout['groups'] = ['g:briefy_scout', ]
        pm = base.copy()
        pm['groups'] = ['g:briefy_pm', ]
        return {
            'customer': BaseUser(
                user_id='669a99c2-9bb3-443f-8891-e600a15e3c10',
                data=customer
            ),
            'professional': BaseUser(
                user_id='769a99c2-9bb3-443f-8891-e600a15e3c10',
                data=professional
            ),
            'system': BaseUser(
                user_id='679a99c2-9bb3-443f-8891-e600a15e3c10',
                data=system
            ),
            'qa': BaseUser(
                user_id='999a99c2-9bb3-443f-8891-e600a15e3c10',
                data=qa
            ),
            'scout': BaseUser(
                user_id='199a99c2-9bb3-443f-8891-e600a15e3c10',
                data=scout
            ),
            'pm': BaseUser(
                user_id='139a99c2-9bb3-443f-8891-e600a15e3c10',
                data=pm
            ),
        }


    def test_workflow(self, instance_obj):
        """Test workflow for this model."""
        from briefy.common.workflow.exceptions import WorkflowTransitionException

        roles = self.get_roles()
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
        assert job.state == 'validation'
        # And now customer is not able to move the object anymore
        assert len(wf.transitions) == 0

        # System will invalidate the submission
        wf.context = roles['system']
        wf.invalidate()
        assert job.state == 'edit'

        # Customer now can edit the job and submit it again
        wf.context = roles['customer']
        assert len(wf.transitions) == 1
        wf.submit()
        assert job.state == 'validation'

        # System will validate the submission
        wf.context = roles['system']
        wf.validate()
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

        job.state == 'awaiting_assets'

        # Professional upload new assets and QA approves it
        wf.context = roles['professional']
        wf.upload()

        job.number_of_photos = 0
        wf.context = roles['qa']
        wf.approve()
        job.state == 'approved'
        assert 'retract_approval' in wf.transitions

        # System or PM can move job to completed
        wf.context = roles['system']
        assert 'complete' in wf.transitions

        wf.context = roles['pm']
        assert 'complete' in wf.transitions

        # Customer can approve or reject the job
        wf.context = roles['customer']
        assert 'complete' in wf.transitions
        assert 'customer_reject' in wf.transitions
        wf.customer_reject(message='Need a picture of the pool')
        # PM could decide to move job to complete or send it back to QA
        wf.context = roles['pm']
        assert 'complete' in wf.transitions
        assert 'retract_approval' in wf.transitions

        # Customer could also move the job to completed from here
        wf.context = roles['customer']
        assert 'complete' in wf.transitions
        wf.complete()
        job.state == 'completed'

        # After completion, only the system can execute a transition to the job
        for role in ('customer', 'professional', 'pm', 'qa', 'scout'):
            wf.context = roles[role]
            assert len(wf.transitions) == 0

        # System can execute a deliver transition
        wf.context = roles['system']
        assert 'deliver' in wf.transitions
        wf.deliver()
