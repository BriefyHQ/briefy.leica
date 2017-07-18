"""Test Task to notify assignments before shooting."""
from briefy.leica import models
from briefy.leica.config import BEFORE_SHOOTING_SECONDS
from briefy.leica.tasks.assignment import _notify_before_shooting
from briefy.leica.tasks.assignment import BEFORE_SHOOTING_MSG
from briefy.leica.tasks.assignment import notify_before_shooting
from conftest import BaseTaskTest
from datetime import timedelta

import json


class TestNotifyAssignmentBeforeShooting(BaseTaskTest):
    """Test notify Assignment before shooting."""

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

    def test_failure_public_notify(self, instance_obj, now_utc):
        """Will ignore assignment because its state and scheduled_datetime is not the expected one.

        Assignment State is not scheduled.
        """
        assignment = instance_obj
        assignment.scheduled_datetime = now_utc + timedelta(seconds=3600)
        notify_before_shooting()

        messages = self.get_messages_from_queue()
        assert len(messages) == 0

        assignment.scheduled_datetime = now_utc - timedelta(
            seconds=int(BEFORE_SHOOTING_SECONDS) - 3600
        )
        assignment.state = 'pending'
        notify_before_shooting()

        messages = self.get_messages_from_queue()
        assert len(messages) == 0

    def test_success_protected_notify(self, instance_obj, now_utc):
        """Will be successful if conditions are met.

        Assignment State is scheduled
        Assignment now >= scheduled_datetime >= BEFORE_SHOOTING_SECONDS
        """
        assignment = instance_obj
        assignment_id = assignment.id

        # do not notify with wrong status or scheduled datetime
        assignment.scheduled_datetime = now_utc + timedelta(seconds=3600)
        assignment.state = 'pending'
        status = _notify_before_shooting(assignment)
        assert status is False

        # now we make sure status and scheduled datetime is correct
        assignment.state = 'scheduled'
        assignment.scheduled_datetime = now_utc - timedelta(
            seconds=int(BEFORE_SHOOTING_SECONDS) - 3600
        )
        status = _notify_before_shooting(assignment)

        assert status is True
        messages = self.get_messages_from_queue()
        assert len(messages) == 1
        for message in messages:
            body = json.loads(message.body)
            assert body['event_name'] in (
                'leica.task.notify_before_shooting.success'
            )

        assignment = models.Assignment.get(assignment_id)
        assert assignment.comments[0].content == BEFORE_SHOOTING_MSG

        # assert next time it will not notify again
        status = _notify_before_shooting(assignment)
        assert status is False
