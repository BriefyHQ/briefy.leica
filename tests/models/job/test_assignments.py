"""Test Assignments database model."""
from briefy.common.db import datetime_utcnow
from briefy.common.workflow.exceptions import WorkflowTransitionException
from briefy.leica import models
from conftest import BaseModelTest
from datetime import timedelta

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestAssignmentModel(BaseModelTest):
    """Test Assignment."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Order, 'data/orders.json'),
        (models.Pool, 'data/jpools.json'),
    ]
    file_path = 'data/assignments.json'
    model = models.Assignment

    @staticmethod
    def prepare_obj_wf(obj, web_request, role=None, state=None):
        """Prepare the instance obj to transition test."""
        if state:
            obj.state = state
        obj.request = web_request
        wf = obj.workflow
        order_wf = obj.order.workflow
        if role:
            web_request.user = role
            wf.context = role
            order_wf.context = role
        return obj, wf, web_request

    @pytest.mark.parametrize('origin_state', ['created'])
    @pytest.mark.parametrize('role_name', ['customer', 'qa', 'system', 'support'])
    def test_workflow_submit(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow submit transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.submit()

        # Validation happened already
        assert assignment.state == 'pending'

    @pytest.mark.parametrize('origin_state', ['pending'])
    @pytest.mark.parametrize('role_name', ['customer', 'pm', 'scout', 'system'])
    def test_workflow_publish(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow publish transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        assignment.order.availability = []
        fields_payload = {
            'pool_id': '58cbcdf7-47f7-4a10-9cbb-64888dbc645a'
        }
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.publish(fields=fields_payload)
        assert 'Order has no availability' in str(excinfo)
        assignment.order.availability = [
            '2027-10-12T12:00:00+00:00',
            '2027-10-13T12:00:00+00:00',
        ]
        wf.publish(fields=fields_payload)
        assert assignment.state == 'published'

    @pytest.mark.parametrize('origin_state', ['published'])
    @pytest.mark.parametrize('role_name', ['customer', 'pm', 'scout'])
    def test_workflow_retract(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow retract transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.retract()
        assert assignment.state == 'pending'
        assert assignment.order.availability == []

    @pytest.mark.parametrize('origin_state', ['published'])
    @pytest.mark.parametrize('role_name', ['professional'])
    def test_workflow_self_assign(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow self_assign transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        order = assignment.order
        order.state = 'received'
        order.availability = [
            '2027-10-12T12:00:00+00:00',
            '2027-10-13T12:00:00+00:00',
        ]

        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.self_assign()
        assert 'Field scheduled_datetime is required for this transition.' in str(excinfo)

        fields_payload = {
            'scheduled_datetime': datetime_utcnow() + timedelta(10),
            'professional_id': '23d94a43-3947-42fc-958c-09245ecca5f2'
        }
        wf.self_assign(fields=fields_payload)

        assert assignment.state == 'scheduled'

    @pytest.mark.parametrize('origin_state', ['published'])
    @pytest.mark.parametrize('role_name', ['pm', 'scout', 'system'])
    def test_workflow_assign_pool(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow assign_pool transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        order = assignment.order
        order.state = 'received'
        order.availability = [
            '2027-10-12T12:00:00+00:00',
            '2027-10-13T12:00:00+00:00',
        ]

        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.assign_pool()
        assert 'Field scheduled_datetime is required for this transition.' in str(excinfo)

        fields_payload = {
            'scheduled_datetime': datetime_utcnow() + timedelta(10),
            'professional_id': '23d94a43-3947-42fc-958c-09245ecca5f2'
        }
        wf.assign_pool(fields=fields_payload)

        assert assignment.state == 'scheduled'

    @pytest.mark.parametrize('origin_state', ['pending'])
    @pytest.mark.parametrize('role_name', ['scout', 'qa', 'pm', 'system'])
    def test_workflow_assign(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow assign transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        # Order needs to be on the correct state as well
        order = assignment.order
        order.state = 'received'

        fields_payload = {
            'professional_id': '23d94a43-3947-42fc-958c-09245ecca5f2',
            'payout_value': 12000,
            'payout_currency': 'EUR',
            'travel_expenses': 1000,
        }
        wf.assign(fields=fields_payload)

        assert assignment.state == 'assigned'
        for key, value in fields_payload.items():
            assert getattr(assignment, key) == value

    @pytest.mark.parametrize('origin_state', ['assigned'])
    @pytest.mark.parametrize('role_name', ['customer', ])
    def test_workflow_cancel_from_assigned(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow cancel transition from assigned."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.cancel()

        assert assignment.state == 'cancelled'
        assert assignment.payout_value == 0
        assert assignment.travel_expenses == 0

    @pytest.mark.parametrize('origin_state', ['assigned'])
    @pytest.mark.parametrize('role_name', ['professional', ])
    def test_workflow_scheduling_issues(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow scheduling_issues transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        assignment.professional_id = '23d94a43-3947-42fc-958c-09245ecca5f2'
        assignment.payout_value = 12000
        assignment.payout_currency = 'EUR'
        assignment.travel_expenses = 1000

        wf.scheduling_issues(
            message='Problem with this Schedule.',
            fields={'additional_message': 'Please ask for a new date.'}
        )

        # assignment will still be assigned
        assert assignment.state == 'assigned'

    @pytest.mark.parametrize('origin_state', ['assigned'])
    @pytest.mark.parametrize('role_name', ['professional', 'pm', 'scout', 'system'])
    def test_workflow_schedule(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow schedule transition."""
        now = datetime_utcnow()
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        if role_name == 'professional':
            scheduled_datetime = now
            with pytest.raises(WorkflowTransitionException) as excinfo:
                wf.schedule(fields={'scheduled_datetime': scheduled_datetime})

            assert 'Shoot time should be at least one day in the future' in str(excinfo)

        scheduled_datetime = now + timedelta(10)
        wf.schedule(
            fields={'scheduled_datetime': scheduled_datetime}
        )
        assert assignment.state == 'scheduled'

    @pytest.mark.parametrize('origin_state', ['scheduled'])
    @pytest.mark.parametrize('role_name', ['professional', 'pm'])
    def test_workflow_reschedule(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow reschedule transition."""
        now = datetime_utcnow()
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        order = assignment.order
        order.state = 'scheduled'

        if role_name == 'professional':
            scheduled_datetime = now
            with pytest.raises(WorkflowTransitionException) as excinfo:
                wf.reschedule(fields={'scheduled_datetime': scheduled_datetime})

            assert 'Shoot time should be at least one day in the future' in str(excinfo)

        scheduled_datetime = now + timedelta(10)
        wf.reschedule(
            fields={'scheduled_datetime': scheduled_datetime}
        )
        assert assignment.state == 'scheduled'
        assert assignment.scheduled_datetime == scheduled_datetime
        assert order.scheduled_datetime == scheduled_datetime

    @pytest.mark.parametrize('origin_state', ['scheduled', 'awaiting_assets'])
    @pytest.mark.parametrize('role_name', ['pm', 'customer'])
    def test_workflow_remove_schedule(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow remove_schedule transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        order = assignment.order
        order.state = 'received'
        order.availability = [
            '2027-10-12T12:00:00+00:00',
            '2027-10-13T12:00:00+00:00',
        ]
        assignment.submission_path = 'https://drive.google.com/folders/0BwrdIL719n7waUlleFJfZ1RGak0'
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.remove_schedule()
        assert 'Assets are already on the system.' in str(excinfo)

        assignment.submission_path = ''
        wf.remove_schedule()

        assert assignment.state == 'assigned'
        assert assignment.scheduled_datetime is None
        assert order.scheduled_datetime is None

    @pytest.mark.parametrize('origin_state', ['scheduled'])
    @pytest.mark.parametrize('role_name', ['customer', ])
    def test_workflow_cancel_from_scheduled(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow cancel transition from scheduled."""
        now = datetime_utcnow()
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        # Will not be available if in the past
        scheduled_datetime = now - timedelta(1)
        assignment.scheduled_datetime = scheduled_datetime
        assert 'cancel' not in wf.transitions

        # Will not be available if in the past
        scheduled_datetime = now + timedelta(10)
        assignment.scheduled_datetime = scheduled_datetime
        assert 'cancel' in wf.transitions

    @pytest.mark.parametrize('origin_state', ['scheduled'])
    @pytest.mark.parametrize('role_name', ['system', ])
    def test_workflow_ready_for_upload(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow ready_for_upload transition from scheduled.

        System is now able to move the assignment to awaiting for assets
        """
        now = datetime_utcnow()
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        assignment.scheduled_datetime = now + timedelta(1)
        assert 'ready_for_upload' in wf.transitions
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.ready_for_upload()
        assert 'Scheduled date time needs to be in the past.' in str(excinfo)

        # Set scheduled date time to be in the past
        assignment.scheduled_datetime = now - timedelta(1)
        wf.ready_for_upload()
        assert assignment.state == 'awaiting_assets'
        scheduled_datetime = now + timedelta(10)
        assignment.scheduled_datetime = scheduled_datetime

    @pytest.mark.parametrize('origin_state', ['awaiting_assets'])
    @pytest.mark.parametrize('role_name', ['customer', ])
    def test_workflow_cancel_from_awaiting_assets(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow cancel transition from awaiting_assets.

        Customer can cancel this assignment before first upload to in_qa.
        """
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        assert 'cancel' in wf.transitions

    @pytest.mark.parametrize('origin_state', ['awaiting_assets'])
    @pytest.mark.parametrize('role_name', ['professional', 'pm', ])
    def test_workflow_upload(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow upload transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        wf.upload(
            fields={
                'submission_path':
                'https://drive.google.com/drive/folders/0BwrdIL719n7waUlleFJfZ1RGak0'
            }
        )
        assert assignment.state == 'asset_validation'

    @pytest.mark.parametrize('origin_state', ['asset_validation'])
    @pytest.mark.parametrize('role_name', ['system', 'qa', ])
    def test_workflow_invalidate_assets(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow invalidate_assets transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        order = assignment.order
        order.state = 'scheduled'
        wf.invalidate_assets(message='Invalidated by Ms. Laure')
        assert assignment.state == 'awaiting_assets'

    @pytest.mark.parametrize('origin_state', ['asset_validation'])
    @pytest.mark.parametrize('role_name', ['system', 'qa', ])
    def test_workflow_validate_assets(
        self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow validate_assets transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        order = assignment.order
        order.state = 'scheduled'
        wf.validate_assets(message='Validated by Ms. Laure')
        assert assignment.state == 'in_qa'
        assert order.state == 'in_qa'

    @pytest.mark.parametrize('origin_state', ['in_qa'])
    @pytest.mark.parametrize('role_name', ['customer', ])
    def test_workflow_cancel_from_in_qa(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow cancel transition from in_qa.

        Customer cannot cancel this assignment after in_qa.
        """
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        assert 'cancel' not in wf.transitions

    @pytest.mark.parametrize('origin_state', ['in_qa'])
    @pytest.mark.parametrize('role_name', ['qa', ])
    def test_workflow_assign_qa_manager(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow assign_qa_manager transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.assign_qa_manager(
            message='Setting a new QA Manager',
            fields={'assignment_internal_qa': ['44f57cff-3db4-4b10-b9dc-8cd8761a6c7e']}
        )
        assert assignment.state == 'in_qa'
        assert '44f57cff-3db4-4b10-b9dc-8cd8761a6c7e' in assignment.assignment_internal_qa
        assert len(assignment.assignment_internal_qa) == 1

    @pytest.mark.parametrize('origin_state', ['in_qa'])
    @pytest.mark.parametrize('role_name', ['qa', ])
    def test_workflow_reject(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow reject transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.reject()
        assert 'Message is required' in str(excinfo)
        wf.reject(message='Missing 5 or 6 pictures',)

    @pytest.mark.parametrize('origin_state', ['awaiting_assets'])
    @pytest.mark.parametrize('role_name', ['qa', ])
    def test_workflow_retract_rejection(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow retract_rejection transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        order = assignment.order
        order.state = 'scheduled'
        fields_payload = {
            'submission_path': 'https://drive.google.com/folders/0BwrdIL719n7waUlleFJfZ1RGak0'
        }
        wf.retract_rejection(fields=fields_payload)

        assert assignment.state == 'in_qa'

    @pytest.mark.parametrize('origin_state', ['in_qa'])
    @pytest.mark.parametrize('role_name', ['qa', ])
    def test_workflow_start_post_process(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow start_post_process transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.start_post_process()

        assert assignment.state == 'post_processing'

    @pytest.mark.parametrize('origin_state', ['in_qa'])
    @pytest.mark.parametrize('role_name', ['qa', 'pm', 'system'])
    def test_workflow_perm_reject(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow perm_reject transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        fields_payload = {
            'additional_compensation': 0,
            'reason_additional_compensation': ''
        }

        wf.perm_reject(fields=fields_payload)

        assert assignment.state == 'perm_rejected'

    @pytest.mark.parametrize('origin_state', ['post_processing'])
    @pytest.mark.parametrize('role_name', ['qa', ])
    def test_workflow_retract_post_process(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow retract_post_process transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.retract_post_process()

        assert assignment.state == 'in_qa'

    @pytest.mark.parametrize('origin_state', ['in_qa', 'post_processing'])
    @pytest.mark.parametrize('role_name', ['qa', ])
    def test_workflow_approve(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow approve transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        if origin_state == 'post_processing':
            # try to approve without archive URL will be blocked
            assignment.order.delivery = None
            with pytest.raises(WorkflowTransitionException) as excinfo:
                wf.approve(
                    fields={
                        'customer_message': ''
                    }
                )
            assert 'Can not approve without Archive URL' in str(excinfo)

        assignment.order.delivery = {
            'archive': 'https://drive.google.com/drive/folders/0BwrdIL719n7waUlleFJfZ1RGak0',
        }
        wf.approve(fields={'customer_message': 'Delivered.'})
        assert assignment.state == 'approved'
        assert 'retract_approval' in wf.transitions

    @pytest.mark.parametrize('origin_state', ['approved'])
    @pytest.mark.parametrize('role_name', ['qa', ])
    def test_workflow_retract_approval(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow retract_approval transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.retract_approval()

        assert assignment.state == 'in_qa'

    @pytest.mark.parametrize('origin_state', ['approved'])
    @pytest.mark.parametrize('role_name', ['system', 'pm'])
    def test_workflow_complete(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow complete transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.complete()

        assert assignment.state == 'completed'

    @pytest.mark.parametrize('origin_state', ['approved'])
    @pytest.mark.parametrize('role_name', ['customer', ])
    def test_workflow_refuse(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow refuse transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.refuse(message='Need a picture of the pool')

        assert assignment.state == 'refused'

    @pytest.mark.parametrize('origin_state', ['refused'])
    @pytest.mark.parametrize('role_name', ['pm'])
    def test_workflow_complete_from_refused(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow complete transition from refused."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        wf.complete()

        assert assignment.state == 'completed'

    @pytest.mark.parametrize('origin_state', ['refused'])
    @pytest.mark.parametrize('role_name', ['pm'])
    def test_workflow_return_to_qa(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow return_to_qa transition."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        order = assignment.order
        order.state = 'refused'
        wf.return_to_qa()

        assert assignment.state == 'in_qa'

    @pytest.mark.parametrize('origin_state', ['cancelled', 'completed', 'perm_rejected'])
    @pytest.mark.parametrize('role_name', ['finance', 'system', 'support'])
    def test_workflow_edit_compensation_from_final_states(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow edit_compensation transition during final states."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        compensation_fields = {
            'additional_compensation': 3000,
            'reason_additional_compensation': 'Post processing',
        }
        wf.edit_compensation(fields=compensation_fields)

        assert assignment.state == origin_state

    @pytest.mark.parametrize('origin_state', ['assigned', 'in_qa'])
    @pytest.mark.parametrize('role_name', ['pm'])
    def test_workflow_edit_compensation_from_pending_states(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow edit_compensation transition during pending states."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        compensation_fields = {
            'additional_compensation': 3000,
            'reason_additional_compensation': 'Post processing',
        }
        wf.edit_compensation(fields=compensation_fields)

        assert assignment.state == origin_state

    @pytest.mark.parametrize('origin_state', ['pending', 'published'])
    @pytest.mark.parametrize('role_name', ['scout', 'pm'])
    def test_workflow_edit_payout_from_scout_states(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow edit_payout transition during scout states."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        payout_fields = dict(
            payout_value=12000,
            payout_currency='GBP',
            travel_expenses=5000,
        )
        wf.edit_payout(fields=payout_fields)

        assert assignment.state == origin_state

    @pytest.mark.parametrize('origin_state', ['cancelled', 'completed', 'perm_rejected'])
    @pytest.mark.parametrize('role_name', ['finance', 'system', 'support'])
    def test_workflow_edit_payout_from_final_states(
            self, instance_obj, web_request, roles, role_name, origin_state
    ):
        """Test Assignment workflow edit_payout transition during final states."""
        assignment, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        payout_fields = dict(
            payout_value=12000,
            payout_currency='GBP',
            travel_expenses=5000,
        )
        wf.edit_payout(fields=payout_fields)

        assert assignment.state == origin_state
