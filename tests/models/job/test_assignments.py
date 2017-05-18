"""Test Assignments database model."""
from briefy.common.db import datetime_utcnow
from briefy.leica import models
from conftest import BaseModelTest
from datetime import timedelta
from pyramid.testing import DummyRequest

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
        from briefy.common.workflow.exceptions import WorkflowPermissionException

        now = datetime_utcnow()
        request = DummyRequest()
        assignment = instance_obj
        assignment.request = request
        wf = assignment.workflow
        order = assignment.order
        order.request = request
        order_wf = order.workflow

        # Object starts as created
        assert assignment.state == 'created'

        # Customer can move it to validation
        wf.context = roles['customer']
        request.user = roles['customer']
        assert 'submit' in wf.transitions
        # System as well
        wf.context = roles['system']
        request.user = roles['system']
        assert 'submit' in wf.transitions
        # PM cannot
        wf.context = roles['pm']
        request.user = roles['pm']
        assert 'submit' in wf.transitions

        # Customer moves it to validation
        wf.context = roles['customer']
        request.user = roles['customer']
        wf.submit()

        # Validation happened already
        assert assignment.state == 'pending'

        # Customer or PM can publish this assignment to assignment pool
        wf.context = roles['pm']
        request.user = roles['pm']
        assert 'publish' in wf.transitions

        wf.context = roles['customer']
        request.user = roles['customer']
        assert 'publish' in wf.transitions

        # Customer can also cancel the assignment
        assert 'cancel' in wf.transitions

        # Scout can assign it to a professional
        wf.context = roles['scout']
        request.user = roles['scout']
        order_wf.context = roles['scout']
        assert 'assign' in wf.transitions
        fields_payload = dict(
            professional_id='23d94a43-3947-42fc-958c-09245ecca5f2',
            payout_value=12000,
            payout_currency='EUR',
            travel_expenses=1000,
        )
        wf.assign(
            fields=fields_payload
        )

        assert assignment.state == 'assigned'
        for key, value in fields_payload.items():
            assert getattr(assignment, key) == value

        # Customer can still cancel the assignment
        wf.context = roles['customer']
        request.user = roles['customer']
        assert 'cancel' in wf.transitions

        # Professional can schedule the assignment or report scheduling issues
        wf.context = roles['professional']
        request.user = roles['professional']
        assert 'schedule' in wf.transitions
        wf.scheduling_issues(
            message='Problem with this Schedule.',
            fields=dict(additional_message='Please ask for a new date.')
        )
        # assignment will still be assigned
        assert assignment.state == 'assigned'

        wf.schedule(
            fields={'scheduled_datetime': now + timedelta(10)}
        )
        assert assignment.state == 'scheduled'

        # Customer can still cancel the assignment
        wf.context = roles['customer']
        request.user = roles['customer']
        assert 'cancel' in wf.transitions

        # System is now able to move the assignment to awaiting for assets
        wf.context = roles['system']
        request.user = roles['system']
        assert 'ready_for_upload' in wf.transitions
        wf.ready_for_upload()
        assert assignment.state == 'awaiting_assets'

        # Customer can cancel this assignment before first upload to in_qa
        wf.context = roles['customer']
        request.user = roles['customer']
        assert 'cancel' in wf.transitions

        # Professional can re-schedule this assignment or send it to qa
        wf.context = roles['professional']
        request.user = roles['professional']
        assert 'reschedule' in wf.transitions
        assert 'upload' in wf.transitions
        wf.upload(
            fields={
                'submission_path':
                'https://drive.google.com/drive/folders/0BwrdIL719n7waUlleFJfZ1RGak0'
            }
        )

        # Customer can not cancel this assignment anymore after upload
        wf.context = roles['customer']
        request.user = roles['customer']
        assert 'cancel' not in wf.transitions

        # QA can reject or approve the assignment
        wf.context = roles['qa']
        request.user = roles['qa']

        # TODO: remove this after automatic Assignment validation
        wf.validate_assets(message='Assets validated.')

        assert 'approve' in wf.transitions
        assert 'reject' in wf.transitions
        # Trying to approve a assignment with the wrong number of assets with raise an exception
        # with pytest.raises(WorkflowTransitionException) as excinfo:
        # TODO: return this when return the approve logic
        # wf.approve()
        # assert 'Incorrect number of assets' in str(excinfo)

        wf.assign_qa_manager(
            message='Setting a new QA Manager',
            fields={'qa_manager': '44f57cff-3db4-4b10-b9dc-8cd8761a6c7e'}
        )

        assert assignment.state == 'in_qa'

        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.reject()
        assert 'Message is required' in str(excinfo)
        wf.reject(
            message='Missing 5 or 6 pictures',
        )

        assert assignment.state == 'awaiting_assets'

        # Professional upload new assets and QA approves it
        wf.context = roles['professional']
        request.user = roles['professional']
        wf.upload(
            fields={
                'submission_path':
                    'https://drive.google.com/drive/folders/0BwrdIL719n7waUlleFJfZ1RGak0'
            }
        )

        assignment.order.number_required_assets = 0
        wf.context = roles['qa']
        request.user = roles['qa']

        # TODO: remove this after automatic Assignment validation
        wf.validate_assets(message='Assets validate.')

        assert 'approve' in wf.transitions
        assert 'start_post_process' in wf.transitions

        wf.start_post_process()
        assert 'approve' in wf.transitions
        assert 'retract_post_process' in wf.transitions
        assert assignment.state == 'post_processing'

        wf.retract_post_process()
        assert assignment.state == 'in_qa'

        wf.approve(
            fields={
                'customer_message': ''
            }
        )
        assert assignment.state == 'approved'
        assert 'retract_approval' in wf.transitions

        # System or PM can move assignment to completed
        wf.context = roles['pm']
        request.user = roles['pm']
        assert 'complete' in wf.transitions
        wf.context = roles['system']
        request.user = roles['system']
        assert 'complete' in wf.transitions

        # Customer can approve or reject the assignment
        wf.context = roles['customer']
        request.user = roles['customer']
        assert 'complete' in wf.transitions
        assert 'refuse' in wf.transitions
        wf.refuse(message='Need a picture of the pool')

        assert assignment.state == 'refused'

        # PM could decide to move assignment to complete or send it back to QA
        wf.context = roles['pm']
        request.user = roles['pm']
        order_wf.context = roles['pm']
        assert 'return_to_qa' in wf.transitions
        wf.return_to_qa()

        # now QA has to approve again
        wf.context = roles['qa']
        request.user = roles['qa']
        assert 'approve' in wf.transitions
        wf.approve(
            fields={'customer_message': ''}
        )

        # now PM can complete or refuse again
        wf.context = roles['pm']
        request.user = roles['pm']
        assert 'complete' in wf.transitions
        assert 'refuse' in wf.transitions

        # Customer could also move the assignment to completed from here
        wf.context = roles['customer']
        request.user = roles['customer']
        assert 'complete' in wf.transitions
        wf.complete()
        assert assignment.state == 'completed'

        # After completion, customer, professional and qa can not do anything
        for role in ('customer', 'professional', 'qa'):
            wf.context = roles[role]
            # two transitions are possible, but the guard should block from these roles
            assert len(wf.transitions) == 0

        # But scout, pm and finance can
        completed_role_map = dict(pm=0, scout=0)
        for role, number in completed_role_map.items():
            wf.context = roles[role]
            # two transitions are possible, but the guard should block from these roles
            assert len(wf.transitions) == number

            payout_fields = dict(
                payout_value=12000,
                payout_currency='GBP',
                travel_expenses=5000,
            )
            with pytest.raises(WorkflowPermissionException) as excinfo:
                wf.edit_payout(fields=payout_fields)
                assert 'Incorrect number of assets' in str(excinfo)

            compensation_fields = dict(
                additional_compensation=3000,
                reason_additional_compensation='Post processing',
            )
            with pytest.raises(WorkflowPermissionException) as excinfo:
                wf.edit_compensation(fields=compensation_fields)
                assert 'Incorrect number of assets' in str(excinfo)
