"""Test Task to move assignments to awaiting_asset state."""
from briefy.leica import models
from briefy.leica.tasks.assignment import _move_assignment_awaiting_assets
from briefy.leica.tasks.assignment import move_assignments_awaiting_assets
from conftest import BaseTaskTest
from datetime import datetime
from pytz import utc

import json
import mock


class TestMoveAssignmentToAwaitingAssets(BaseTaskTest):
    """Test Move Assignment to Awaiting Assets task."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Pool, 'data/jpools.json'),
        (models.Project, 'data/projects.json'),
        (models.Order, 'data/orders.json'),
    ]

    payload_position = -1
    file_path = 'data/assignments.json'
    model = models.Assignment

    def test_wrong_state(self, instance_obj):
        """Will ignore the assignment because its state is not the expected one.

        Assignment State is not on scheduled
        """
        assignment = instance_obj
        status = _move_assignment_awaiting_assets(assignment=assignment)

        assert status is False
        messages = self.get_messages_from_queue()
        assert len(messages) == 0

    def test_success(self, instance_obj):
        """Will be successful if conditions are met.

        Assignment State is scheduled
        Assignment scheduled_datetime is in the past
        """
        assignment = instance_obj
        assignment_id = assignment.id
        assignment.state = 'scheduled'
        assignment.scheduled_datetime = datetime(2016, 9, 1, 12, 0, 0, tzinfo=utc)
        status = _move_assignment_awaiting_assets(assignment=assignment)

        assert status is True
        messages = self.get_messages_from_queue()
        assert len(messages) == 2
        for message in messages:
            body = json.loads(message.body)
            assert body['event_name'] in (
                'assignment.workflow.ready_for_upload',
                'leica.task.assignment_awaiting_assets.success'
            )

        assignment = models.Assignment.get(assignment_id)

        assert assignment.state == 'awaiting_assets'

    def test_move_assignments_awaiting_assets(self, instance_obj):
        """Test move_assignments_awaiting_assets."""
        assignment = instance_obj
        assignment.state = 'scheduled'
        assignment.scheduled_datetime = datetime(2016, 9, 1, 12, 0, 0, tzinfo=utc)

        move_assignments_awaiting_assets()
        messages = self.get_messages_from_queue()
        assert len(messages) == 0

    def test_wrong_assignment_state(self, instance_obj):
        """Will not move the order because an Assignment is not in a correct state."""
        from briefy.common.workflow.exceptions import WorkflowTransitionException

        assignment = instance_obj
        assignment_id = assignment.id
        assignment.state = 'scheduled'
        assignment.scheduled_datetime = datetime(2016, 9, 1, 12, 0, 0, tzinfo=utc)

        method = 'briefy.leica.models.job.workflows.AssignmentWorkflow.ready_for_upload'
        with mock.patch(method) as mock_transition:
            mock_transition.side_effect = WorkflowTransitionException()
            status = _move_assignment_awaiting_assets(assignment=assignment)

        assert status is False
        messages = self.get_messages_from_queue()
        assert len(messages) == 1
        for message in messages:
            body = json.loads(message.body)
            assert body['event_name'] in (
                'leica.task.assignment_awaiting_assets.failure'
            )

        assignment = models.Assignment.get(assignment_id)

        assert assignment.state == 'scheduled'
