"""Test LeadOrder database model."""
from briefy.common.workflow.exceptions import WorkflowTransitionException
from briefy.leica import models
from briefy.leica.events.assignment import AssignmentCreatedEvent
from briefy.leica.events.leadorder import LeadOrderCreatedEvent
from briefy.leica.subscribers.assignment import assignment_created_handler
from briefy.leica.subscribers.leadorder import leadorder_created_handler
from conftest import BaseModelTest
from datetime import timedelta

import pytest
import pytz
import uuid


@pytest.mark.usefixtures('create_dependencies')
class TestLeadOrderModel(BaseModelTest):
    """Test LeadOrder."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json')
    ]
    file_path = 'data/leadorders.json'
    model = models.LeadOrder
    initial_wf_state = 'new'

    @staticmethod
    def prepare_obj_wf(obj, web_request, role=None, state=None):
        """Prepare the instance obj to transition test."""
        if state:
            obj.state = state
        obj.request = web_request
        wf = obj.workflow
        if role:
            web_request.user = role
            wf.context = role
        return obj, wf, web_request

    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system', 'bizdev'])
    def test_workflow_submit(self, instance_obj, roles, web_request, session, role_name):
        """Test workflow submit after leadorder creation."""
        leadorder, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            'created',
        )

        # manually execute the order created handler
        event = LeadOrderCreatedEvent(leadorder, web_request)
        leadorder_created_handler(event)
        event()
        session.flush()

        assert leadorder.assignment is None
        assert 'submit' not in wf.transitions
        assert leadorder.state == 'new'
        assert leadorder.price
        assert leadorder.price_currency

        received_transitions = (
            'confirm',
            'edit_location',
            'edit_requirements',
            'cancel'
        )
        for transition in received_transitions:
            assert transition in wf.transitions

        # Check if assignment was created
        assignment = leadorder.assignments[-1]
        event = AssignmentCreatedEvent(assignment, request)
        assignment_created_handler(event)
        event()
        session.flush()

        assert assignment.state == 'pending'
        assert leadorder.state_history[-1]['transition'] == 'submit'

    @pytest.mark.parametrize('file_path', ['data/order_locations.json'])
    @pytest.mark.parametrize('position', [0])
    @pytest.mark.parametrize('origin_state', ['new', 'received', 'assigned', 'scheduled'])
    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system'])
    def test_workflow_edit_location(
        self, instance_obj, session, web_request, roles, role_name, origin_state, obj_payload_other
    ):
        """Test LeadOrder workflow edit_location transition."""
        location_payload = obj_payload_other
        leadorder, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.edit_location()
            assert 'Field location is required for this transition' in str(excinfo)

        # delete previous existing order location before adding a new one
        if leadorder.location:
            session.delete(leadorder.location)
            session.flush()

        # add a new location to the order
        location_payload['order_id'] = leadorder.id
        location_payload['id'] = str(uuid.uuid4())
        location = models.OrderLocation(**location_payload)
        leadorder.location = location
        session.add(location)
        session.flush()
        new_location_payload = {
            'location': {
                'first_name': 'J.  ',
                'last_name': 'Hartman-Zwiers',
                'order_id': str(leadorder.id),
                'mobile': '+33 31356240391',
                'email': 'info@sdlyonne.com',
                'timezone': 'Europe/Berlin',
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
                'id': location_payload['id'],
                'coordinates': [
                    52.4907727,
                    13.432224399999996
                ]
            }
        }
        wf.edit_location(fields=new_location_payload)
        session.flush()

        assert leadorder.state == origin_state
        assert leadorder.state_history[-1]['transition'] == 'edit_location'

        location_payload = new_location_payload['location']
        for key, value in location_payload.items():
            if key == 'info':
                info_payload = location_payload['info']
                for ikey, ivalue in info_payload.items():
                    assert leadorder.location.info[ikey] == ivalue
            elif key == 'coordinates':
                coordinates = getattr(leadorder.location, key)
                coordinates['coordinates'] == value
            else:
                assert getattr(leadorder.location, key) == value

    @pytest.mark.parametrize('origin_state', ['new', 'received', 'assigned', 'scheduled'])
    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system'])
    def test_workflow_edit_requirements(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test LeadOrder workflow edit_requirementstransition."""
        leadorder, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        new_requirements = {}
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.edit_requirements(fields=new_requirements)

        assert 'Field number_required_assets is required for this transition' in str(excinfo)

        new_requirements['number_required_assets'] = 20
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.edit_requirements(fields=new_requirements)

        assert 'Field requirements is required for this transition' in str(excinfo)

        new_requirements['requirements'] = 'New requirements for this order!'
        wf.edit_requirements(fields=new_requirements)
        session.flush()

        assert leadorder.state == origin_state
        assert leadorder.state_history[-1]['transition'] == 'edit_requirements'
        for key, value in new_requirements.items():
            assert getattr(leadorder, key) == value

    @pytest.mark.parametrize('origin_state', ['new'])
    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system'])
    def test_workflow_confirm(
        self, instance_obj, web_request, session, roles, role_name, now_utc, origin_state
    ):
        """Test LeadOrder workflow confirm transition."""
        leadorder, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        now_utc = now_utc.astimezone(pytz.timezone(leadorder.timezone))

        new_availability = {}
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.confirm(fields=new_availability)

        assert 'Field availability is required for this transition' in str(excinfo)

        availability_1 = now_utc + timedelta(1)
        availability_2 = now_utc + timedelta(2)
        new_availability['availability'] = [
            availability_1.isoformat(),
            availability_2.isoformat()
        ]

        # PMs can set any date but others do not
        if role_name != 'pm':
            with pytest.raises(WorkflowTransitionException) as excinfo:
                wf.confirm(fields=new_availability)

            assert 'Both availability dates must be at least 7 days from now' in str(excinfo)

        availability_1 = now_utc + timedelta(8)
        availability_2 = now_utc + timedelta(10)

        new_availability['availability'] = [
            availability_1.isoformat(),
            availability_2.isoformat()
        ]
        wf.confirm(fields=new_availability)
        session.flush()
        if origin_state == 'new':
            destination_state = 'received'
        else:
            destination_state = origin_state

        assert leadorder.state == destination_state
        assert leadorder.state_history[-1]['transition'] == 'confirm'
        for key, value in new_availability.items():
            assert getattr(leadorder, key) == value

        # should work also with normal python datetime instances
        new_availability['availability'] = [
            availability_1,
            availability_2,
        ]
        leadorder, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        wf.confirm(fields=new_availability)
        session.flush()

        assert leadorder.state == destination_state
        for key, value in new_availability.items():
            assert getattr(leadorder, key)[0] == value[0].isoformat()
            assert getattr(leadorder, key)[1] == value[1].isoformat()

    @pytest.mark.parametrize('origin_state', ['new', 'received', 'assigned', 'scheduled'])
    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system'])
    def test_workflow_cancel(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test LeadOrder workflow cancel transition."""
        leadorder, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state,
        )

        assignment = leadorder.assignments[-1]
        assignment, ass_wf, request = self.prepare_obj_wf(
            assignment,
            web_request,
            roles[role_name],
            'pending'
        )

        message = 'Order cancelled'
        leadorder.workflow.cancel(message=message)
        session.flush()

        assert leadorder.state == 'cancelled'
        assert leadorder.state_history[-1]['transition'] == 'cancel'
        assert leadorder.state_history[-1]['message'] == message
        assert leadorder.comments[-1].content == message
        assert assignment.state == 'cancelled'
        assert assignment.state_history[-1]['transition'] == 'cancel'
        assert assignment.payout_value == 0
        assert assignment.scheduled_datetime is None
