"""Test Task to notify assignment late submission."""
from briefy.leica import models
from briefy.leica.config import LATE_SUBMISSION_SECONDS
from briefy.leica.tasks.assignment import _notify_late_submissions
from briefy.leica.tasks.assignment import LATE_SUBMISSION_MSG
from briefy.leica.tasks.assignment import notify_late_submissions
from conftest import BaseTaskTest
from datetime import timedelta

import json


class TestNotifyAssignmentNotSubmitted(BaseTaskTest):
    """Test notify Assignment not submitted 48hs after shooting."""

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

    def test_wrong_state_scheduled_datetime(self, instance_obj, now_utc):
        """Will ignore assignment because its state and scheduled_datetime is not the expected one.

        Assignment State is not awaiting assets.
        """
        assignment = instance_obj
        assignment.scheduled_datetime = now_utc
        notify_late_submissions()

        messages = self.get_messages_from_queue()
        assert len(messages) == 0

        assignment.scheduled_datetime = now_utc + timedelta(
            seconds=int(LATE_SUBMISSION_SECONDS) + 60
        )
        assignment.state = 'pending'
        notify_late_submissions()

        messages = self.get_messages_from_queue()
        assert len(messages) == 0

    def test_success(self, instance_obj, now_utc):
        """Will be successful if conditions are met.

        Assignment State is awaiting_assets
        Assignment scheduled_datetime is more than 48hs in the past
        Assignment has not been notified before
        """
        assignment = instance_obj
        assignment_id = assignment.id

        # do not notify with wrong status or scheduled datetime
        assignment.scheduled_datetime = now_utc
        assignment.state = 'scheduled'
        status = _notify_late_submissions(assignment=assignment)
        assert status is False

        # now we make sure status and scheduled datetime is correct
        assignment.state = 'awaiting_assets'
        assignment.scheduled_datetime = now_utc - timedelta(
            seconds=int(LATE_SUBMISSION_SECONDS) + 3600
        )
        status = _notify_late_submissions(assignment)

        assert status is True
        messages = self.get_messages_from_queue()
        assert len(messages) == 1
        for message in messages:
            body = json.loads(message.body)
            assert body['event_name'] in (
                'leica.task.notify_late_submission.success'
            )

        assignment = models.Assignment.get(assignment_id)
        assert assignment.comments[0].content == LATE_SUBMISSION_MSG

        # assert next time it will not notify again
        status = _notify_late_submissions(assignment)
        assert status is False
