"""Test Assignments database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestAssignmentModel(BaseModelTest):
    """Test Assignment."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Order, 'data/orders.json'),
    ]
    file_path = 'data/assignments.json'
    model = models.Assignment

    def test_workflow(self, instance_obj, roles):
        """Test workflow for this model."""
        from briefy.common.workflow.exceptions import WorkflowTransitionException

        assignment = instance_obj
        wf = assignment.workflow

        # Object starts as created
        assert assignment.state == 'created'

        # Customer can move it to validation
        wf.context = roles['customer']
        assert 'submit' in wf.transitions
        # System as well
        wf.context = roles['system']
        assert 'submit' in wf.transitions
        # PM cannot
        wf.context = roles['pm']
        assert 'submit' in wf.transitions

        # Customer moves it to validation
        wf.context = roles['customer']
        wf.submit()

        # Validation happened already
        assert assignment.state == 'pending'

        # Customer or PM can publish this assignment to assignment pool
        wf.context = roles['pm']
        assert 'publish' in wf.transitions

        wf.context = roles['customer']
        assert 'publish' in wf.transitions

        # Customer can also cancel the assignment
        assert 'cancel' in wf.transitions

        # Scout can assign it to a professional
        wf.context = roles['scout']
        assert 'assign' in wf.transitions
        wf.assign()
        assert assignment.state == 'assigned'

        # Customer can still cancel the assignment
        wf.context = roles['customer']
        assert 'cancel' in wf.transitions

        # Professional can schedule the assignment or report scheduling issues
        wf.context = roles['professional']
        assert 'schedule' in wf.transitions
        wf.scheduling_issues()
        # assignment will still be assigned
        assert assignment.state == 'assigned'

        wf.schedule()
        assert assignment.state == 'scheduled'

        # Customer can still cancel the assignment
        wf.context = roles['customer']
        assert 'cancel' in wf.transitions

        # System is now able to move the assignment to awaiting for assets
        wf.context = roles['system']
        assert 'ready_for_upload' in wf.transitions
        wf.ready_for_upload()
        assert assignment.state == 'awaiting_assets'

        # Customer can cancel this assignment before first upload to in_qa
        wf.context = roles['customer']
        assert 'cancel' in wf.transitions

        # Professional can re-schedule this assignment or send it to qa
        wf.context = roles['professional']
        assert 'reschedule' in wf.transitions
        assert 'upload' in wf.transitions
        wf.upload()

        # Customer can not cancel this assignment anymore after upload
        wf.context = roles['customer']
        assert 'cancel' not in wf.transitions

        # QA can reject or approve the assignment
        wf.context = roles['qa']

        # TODO: remove this after automatic Assignment validation
        wf.validate_assets()

        assert 'approve' in wf.transitions
        assert 'reject' in wf.transitions
        # Trying to approve a assignment with the wrong number of assets with raise an exception
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.approve()

        assert 'Incorrect number of assets' in str(excinfo)
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.reject()
        assert 'Message is required' in str(excinfo)
        wf.reject(message='Missing 5 or 6 pictures')

        assert assignment.state == 'awaiting_assets'

        # Professional upload new assets and QA approves it
        wf.context = roles['professional']
        wf.upload()

        assignment.order.number_required_assets = 0
        wf.context = roles['qa']

        # TODO: remove this after automatic Assignment validation
        wf.validate_assets()

        wf.approve()
        assert assignment.state == 'approved'
        assert 'retract_approval' in wf.transitions

        # System or PM can move assignment to completed
        wf.context = roles['pm']
        assert 'complete' in wf.transitions
        wf.context = roles['system']
        assert 'complete' in wf.transitions

        # Customer can approve or reject the assignment
        wf.context = roles['customer']
        assert 'complete' in wf.transitions
        assert 'refuse' in wf.transitions
        wf.refuse(message='Need a picture of the pool')

        assert assignment.state == 'refused'

        # PM could decide to move assignment to complete or send it back to QA
        wf.context = roles['pm']
        assert 'return_to_qa' in wf.transitions
        wf.return_to_qa()

        # now QA has to approve again
        wf.context = roles['qa']
        assert 'approve' in wf.transitions
        wf.approve()

        # now PM can complete or refuse again
        wf.context = roles['pm']
        assert 'complete' in wf.transitions
        assert 'refuse' in wf.transitions

        # Customer could also move the assignment to completed from here
        wf.context = roles['customer']
        assert 'complete' in wf.transitions
        wf.complete()
        assert assignment.state == 'completed'

        # After completion, only the system can execute a transition to the assignment
        for role in ('customer', 'professional', 'pm', 'qa', 'scout'):
            wf.context = roles[role]
            assert len(wf.transitions) == 0
