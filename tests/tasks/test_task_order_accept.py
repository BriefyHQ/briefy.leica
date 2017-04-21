"""Test Task to move orders to accepted state."""
from briefy.leica import models
from briefy.leica.tasks.order import _move_order_accepted
from briefy.leica.tasks.order import move_orders_accepted
from conftest import BaseTaskTest
from datetime import datetime
from pytz import utc

import json


class TestMoveOrderToAccepted(BaseTaskTest):
    """Test Move Assignment to Pool task."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
    ]

    payload_position = -1
    file_path = 'data/orders.json'
    model = models.Order

    def test_wrong_state(self, instance_obj):
        """Will ignore the order because its state is not the expected one.

        Order State is not on delivered
        """
        order = instance_obj
        status = _move_order_accepted(order=order)

        assert status is False
        messages = self.get_messages_from_queue()
        assert len(messages) == 0

    def test_success(self, instance_obj):
        """Will be successful if conditions are met.

        Order State is delivered
        Order Last Delivery Date happened after the project approval window expired.
        """
        order = instance_obj
        order_id = order.id
        project = order.project
        project.approval_window = 1  # 1 day
        order.state = 'delivered'
        order.last_deliver_date = datetime(2016, 9, 1, 12, 0, 0, tzinfo=utc)
        status = _move_order_accepted(order=order)

        assert status is True
        messages = self.get_messages_from_queue()
        assert len(messages) == 2
        for message in messages:
            body = json.loads(message.body)
            assert body['event_name'] in (
                'order.workflow.accept',
                'leica.task.order_accepted.success'
            )

        order = models.Order.get(order_id)

        assert order.state == 'accepted'

    def test_move_orders_accepted(self, instance_obj):
        """Test move_orders_accepted."""
        order = instance_obj
        order.state = 'delivered'
        move_orders_accepted()
        messages = self.get_messages_from_queue()
        assert len(messages) == 0

    def test_wrong_assignment_state(self, instance_obj):
        """Will not move the order because an Assignment is not in a correct state."""
        assignment = models.Assignment()
        assignment.state = 'created'

        order = instance_obj
        order_id = order.id
        project = order.project
        project.approval_window = 1  # 1 day
        order.state = 'delivered'
        order.last_deliver_date = datetime(2016, 9, 1, 12, 0, 0, tzinfo=utc)
        order.assignments = [assignment, ]
        status = _move_order_accepted(order=order)

        assert status is False
        messages = self.get_messages_from_queue()
        assert len(messages) == 1
        for message in messages:
            body = json.loads(message.body)
            assert body['event_name'] in (
                'leica.task.order_accepted.failure'
            )

        order = models.Order.get(order_id)

        assert order.state == 'delivered'
