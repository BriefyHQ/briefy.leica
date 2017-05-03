"""Test Order database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestOrderModel(BaseModelTest):
    """Test Order."""

    dependencies = [
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json')
    ]
    file_path = 'data/orders.json'
    model = models.Order
    initial_wf_state = 'received'

    def test_workflow_01_submit(self, instance_obj, roles, web_request):
        """Test workflow for this model."""
        order = instance_obj
        order.state = 'created'
        order.request = web_request
        wf = order.workflow

        from briefy.leica.events.order import OrderCreatedEvent
        event = OrderCreatedEvent(order, web_request)
        web_request.registry.notify(event)
        event()

        assert order.assignment is None

        # Customer can move it to validation
        wf.context = roles['customer']
        web_request.user = roles['customer']
        assert 'submit' in wf.transitions

        # System as well
        wf.context = roles['system']
        web_request.user = roles['system']
        assert 'submit' in wf.transitions

        # PM cannot
        wf.context = roles['pm']
        web_request.user = roles['pm']
        assert 'submit' in wf.transitions

        # Customer moves it to validation
        wf.context = roles['customer']
        web_request.user = roles['customer']
        wf.submit()

        # Validation happened already
        assignment = order.assignments[0]

        from briefy.leica.events.assignment import AssignmentCreatedEvent
        event = AssignmentCreatedEvent(assignment, web_request)
        web_request.registry.notify(event)
        event()

        assert assignment.state == 'created'
        assert order.state == 'received'
