"""Test Task to move assignments to a Pool."""
from conftest import BaseTaskTest
from briefy.leica import models
from briefy.leica.tasks.pool import _move_assignment_to_pool
from briefy.leica.tasks.pool import move_assignments_to_pool

import json


class TestMoveAssignmentToPool(BaseTaskTest):
    """Test Move Assignment to Pool task."""

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

    pool = None
    order = None
    assignment = None

    def test_wrong_state(self, instance_obj):
        """Will ignore the assignment because its state is not the expected one.

        Assignment State is not on pending
        """
        assignment = instance_obj
        pool = models.Pool.query().first()
        has_availability = True
        status = _move_assignment_to_pool(
            assignment=assignment,
            pool=pool,
            has_availability=has_availability
        )

        assert status is False
        messages = self.get_messages_from_queue()
        assert len(messages) == 0

    def test_success(self, instance_obj):
        """Will be successful if conditions are met.

        Assignment State is pending
        Order Availability is correct: At least 2 days in the future
        Assignment is not on a pool yet
        Assignmnet have payout information
        """
        pool = models.Pool.query().first()
        assignment = instance_obj
        assignment_id = assignment.id
        assignment.state = 'pending'
        has_availability = True
        status = _move_assignment_to_pool(
            assignment=assignment,
            pool=pool,
            has_availability=has_availability
        )

        assert status is True
        messages = self.get_messages_from_queue()
        assert len(messages) == 2
        for message in messages:
            body = json.loads(message.body)
            assert body['event_name'] in (
                'assignment.workflow.publish',
                'leica.task.assignment_pool.success'
            )

        assignment = models.Assignment.get(assignment_id)

        assert assignment.state == 'published'

    def test_failure_no_availability(self, instance_obj):
        """Will fail if Order Availability is not correct."""
        pool = models.Pool.query().first()
        assignment = instance_obj
        assignment_id = assignment.id
        assignment.state = 'pending'
        has_availability = False
        status = _move_assignment_to_pool(
            assignment=assignment,
            pool=pool,
            has_availability=has_availability
        )

        assert status is False
        messages = self.get_messages_from_queue()
        assert len(messages) == 1
        for message in messages:
            body = json.loads(message.body)
            assert body['event_name'] in (
                'leica.task.assignment_pool.no_availability'
            )

        assignment = models.Assignment.get(assignment_id)

        assert assignment.state == 'pending'

    def test_failure_has_pool_id(self, instance_obj):
        """Will fail if Assignment already has a pool id."""
        pool = models.Pool.query().first()
        pool_id = pool.id
        assignment = instance_obj
        assignment_id = assignment.id
        assignment.state = 'pending'
        assignment.pool_id = pool_id
        has_availability = True
        status = _move_assignment_to_pool(
            assignment=assignment,
            pool=pool,
            has_availability=has_availability
        )

        assert status is False
        messages = self.get_messages_from_queue()
        assert len(messages) == 1
        for message in messages:
            body = json.loads(message.body)
            assert body['event_name'] in (
                'leica.task.assignment_pool.has_pool_id'
            )

        assignment = models.Assignment.get(assignment_id)

        assert assignment.state == 'pending'

    def test_failure_no_payout(self, instance_obj):
        """Will fail if Assignment has no payout."""
        pool = models.Pool.query().first()
        assignment = instance_obj
        assignment_id = assignment.id
        assignment.state = 'pending'
        assignment.payout_value = 0
        assignment.pool_id = None
        has_availability = True
        status = _move_assignment_to_pool(
            assignment=assignment,
            pool=pool,
            has_availability=has_availability
        )

        assert status is False
        messages = self.get_messages_from_queue()
        assert len(messages) == 1
        for message in messages:
            body = json.loads(message.body)
            assert body['event_name'] in (
                'leica.task.assignment_pool.no_payout'
            )

        assignment = models.Assignment.get(assignment_id)

        assert assignment.state == 'pending'

    def test_move_assignments_to_pool(self, instance_obj):
        """Test move_assignments_to_pool."""
        pool = models.Pool.query().first()
        assignment = instance_obj
        order = assignment.order
        project = order.project
        project.pool_id = pool.id
        move_assignments_to_pool()
        messages = self.get_messages_from_queue()
        assert len(messages) == 0
