"""Test Order database model."""
from briefy.leica import models
from briefy.leica.subscribers.assignment import assignment_created_handler
from briefy.leica.subscribers.order import order_created_handler
from conftest import BaseModelTest

import pytest


LOCATION_PAYLOAD = {
    'id': 'd85dc102-7d3b-4574-a261-4bf72db571db',
    'order_id': '011418fa-f450-4deb-b6ea-7f8e103a66d1',
    'updated_at': '2016-09-18T18:55:20.226722+00:00',
    'created_at': '2016-09-18T18:55:20.226696+00:00',
    'state': 'created',
    'locality': 'Berlin',
    'country': 'DE',
    'timezone': 'Europe/Berlin',
    'first_name': 'Jhon',
    'last_name': 'Wayne',
    'mobile': '+4917628607522',
    'info': {
        'additional_info': 'House 3, Entry C, 1st. floor, c/o GLG',
        'province': 'Berlin',
        'locality': 'Berlin',
        'sublocality': 'Kreuzberg',
        'route': 'Schlesische Straße',
        'street_number': '27',
        'country': 'DE',
        'postal_code': '10997'
    },
    'state_history': [
        {
            'to': 'created',
            'transition': '',
            'actor': None,
            'message': None,
            'date': '2016-09-18T18:55:20.224411+00:00',
            'from': ''
        }
    ]
}


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

    @staticmethod
    def prepare_instance_obj_wf(obj, web_request, state=None, role=None):
        """Prepare the instance obj to transition test."""
        obj.state = state
        obj.request = web_request
        wf = obj.workflow
        if role:
            web_request.user = role
            wf.context = role
        return obj, wf, web_request

    def test_workflow_01_submit(self, instance_obj, roles, web_request):
        """Test workflow submit after order creation."""
        order, wf, request = self.prepare_instance_obj_wf(
            instance_obj,
            web_request,
            'created',
            roles['system']
        )

        # manually execute the order created handler
        from briefy.leica.events.order import OrderCreatedEvent
        event = OrderCreatedEvent(order, web_request)
        order_created_handler(event)
        event()

        assert order.assignment is None
        assert 'submit' not in wf.transitions
        assert order.state == 'received'
        assert order.price
        assert order.price_currency

        # Customer transitions
        wf.context = roles['customer']
        request.user = roles['customer']
        received_transitions = ('set_availability', 'edit_location', 'edit_requirements',)
        for transition in received_transitions:
            assert transition in wf.transitions

        # PM transitions
        wf.context = roles['pm']
        request.user = roles['pm']
        for transition in received_transitions:
            assert transition in wf.transitions

        # Check if assignment was created
        assignment = order.assignments[0]

        from briefy.leica.events.assignment import AssignmentCreatedEvent
        event = AssignmentCreatedEvent(assignment, request)
        assignment_created_handler(event)
        event()

        assert assignment.state == 'pending'

    def test_workflow_02_edit_location(self, instance_obj, session):
        """Test Order workflow edit_location transition."""
        order = instance_obj
        wf = order.workflow

        # add a new location to the order
        LOCATION_PAYLOAD['order_id'] = order.id
        location = models.OrderLocation(**LOCATION_PAYLOAD)
        order.location = location
        session.add(location)
        session.flush()
        new_location_payload = {
            'location': {
                'first_name': 'J.  ',
                'last_name': 'Hartman-Zwiers',
                'order_id': str(order.id),
                'mobile': '+33 31356240391',
                'email': 'info@sdlyonne.com',
                'formatted_address': 'Nansenstraße 17, 12047 Berlin, Germany',
                'info': {
                    'route': 'Nansenstraße',
                    'street_number': '17',
                    'province': 'Berlin',
                    'postal_code': '12047',
                    'place_id': 'ChIJ21mMXrFPqEcRPrQdhCoDsHs',
                    'formatted_address': 'Nansenstraße 17, 12047 Berlin, Germany',
                    'coordinates': [
                        52.4907727,
                        13.432224399999996
                    ],
                    'locality': 'Berlin',
                    'country': 'DE'
                },
                'locality': 'Berlin',
                'country': 'DE',
                'id': str(location.id),
                'coordinates': [
                    52.4907727,
                    13.432224399999996
                ]
            }
        }
        fields = new_location_payload
        wf.edit_location(fields=fields)
        session.flush()
        assert order.state == 'received'

        location_payload = new_location_payload['location']
        for key, value in location_payload.items():
            if key == 'info':
                info_payload = location_payload['info']
                for ikey, ivalue in info_payload.items():
                    assert order.location.info[ikey] == ivalue
            elif key == 'coordinates':
                coordinates = getattr(order.location, key)
                coordinates['coordinates'] == value
            else:
                assert getattr(order.location, key) == value
