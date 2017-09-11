"""Test LeadOrder database model."""
from briefy.common.workflow.exceptions import WorkflowTransitionException
from briefy.leica import models
from briefy.leica.events.assignment import AssignmentCreatedEvent
from briefy.leica.events.leadorder import LeadOrderCreatedEvent
from briefy.leica.subscribers.assignment import assignment_created_handler
from briefy.leica.subscribers.leadorder import leadorder_created_handler
from conftest import BaseModelTest
from datetime import timedelta

import mock
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

    def test_actual_order_price_is_equal_to_zero(self, instance_obj):
        """Test if the created object actual_order_price is equal to 0."""
        assert instance_obj.actual_order_price == 0

    def test_confirmation_fields_in_to_dict(self, instance_obj):
        """Test if confirmation_fields is on the to_dict payload."""
        to_dict = instance_obj.to_dict()

        assert 'confirmation_fields' in to_dict
        assert 'availability' in to_dict['confirmation_fields']

    def test_confirmation_fields_in_to_dict_returning_empty_list(self, instance_obj, session):
        """Test if confirmation_fields is on the to_dict payload."""
        project = instance_obj.project
        project.leadorder_confirmation_fields = None
        session.flush()
        to_dict = instance_obj.to_dict()

        assert 'confirmation_fields' in to_dict
        assert isinstance(to_dict['confirmation_fields'], list)
        assert to_dict['confirmation_fields'] == []
        project.leadorder_confirmation_fields = ['availability']
        session.flush()

    @staticmethod
    def delete_assigment_created(assignment, session):
        """Delete assignment created."""
        session.execute("DELETE from assignments_version where id = '{0}'".format(assignment.id))
        session.flush()
        session.query(models.Assignment).filter_by(id=assignment.id).delete()

    @staticmethod
    def notify_assigment_created(assignment, request, session):
        """Notify event of assignment created out of a web request context."""
        event = AssignmentCreatedEvent(assignment, request)
        assignment_created_handler(event)
        event()
        session.flush()

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
        assert leadorder.state_history[-1]['transition'] == 'submit'
        project = leadorder.project
        assert leadorder.price
        assert leadorder.price_currency
        assert leadorder.asset_types == project.asset_types[:1]

        received_transitions = (
            'confirm',
            'edit_location',
            'edit_requirements',
            'cancel'
        )
        for transition in received_transitions:
            assert transition in wf.transitions

        assert len(leadorder.assignments) == 0

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
        leadorder.actual_order_price = 0

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
        message = 'Lead confirmed!'
        wf.confirm(fields=new_availability, message=message)
        session.flush()
        assignment = leadorder.assignments[-1]
        self.notify_assigment_created(assignment, request, session)
        assert assignment.state == 'pending'
        assert assignment.state_history[-1]['transition'] == 'submit'
        assert assignment.asset_types == leadorder.asset_types

        assert leadorder.state_history[-1]['transition'] == 'confirm'
        assert leadorder.state == 'received'
        assert leadorder.state_history[-1]['message'] == message
        for key, value in new_availability.items():
            assert getattr(leadorder, key) == value

        leadorder.availability = None
        session.flush()
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
        # remove previous transition
        leadorder.state_history.pop()

        wf.confirm(fields=new_availability)
        session.flush()
        assignment = leadorder.assignments[-1]
        self.notify_assigment_created(assignment, request, session)

        assert leadorder.state == 'received'
        assert leadorder.actual_order_price == leadorder.price
        assert leadorder.current_type == 'order'
        for key, value in new_availability.items():
            assert getattr(leadorder, key)[0] == value[0].isoformat()
            assert getattr(leadorder, key)[1] == value[1].isoformat()

        leadorder.availability = None
        session.flush()

    @pytest.mark.parametrize('origin_state', ['new'])
    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system'])
    def test_workflow_confirm_without_availability(
        self, instance_obj, web_request, session, roles, role_name, now_utc, origin_state
    ):
        """Test LeadOrder workflow confirm transition without providing availability."""
        leadorder, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        leadorder.actual_order_price = 0
        # Remove the need for availability to be provided for a confirmed lead order
        project = leadorder.project
        project.leadorder_confirmation_fields = []

        wf.confirm()
        assert leadorder.state == 'received'

    @pytest.mark.parametrize('origin_state', ['new'])
    @pytest.mark.parametrize('role_name', ['pm'])
    def test_workflow_confirm_not_enabled(
        self, instance_obj, web_request, session, roles, role_name, now_utc, origin_state
    ):
        """Test LeadOrder workflow confirm transition not enabled."""
        leadorder, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        leadorder.actual_order_price = 0
        # Remove the need for availability to be provided for a confirmed lead order
        project = leadorder.project
        project.leadorder_confirmation_fields = []

        method = 'briefy.leica.models.job.workflows.leadorder.lead_confirmation_enabled'
        with mock.patch(method) as mock_creation:
            mock_creation.return_value = False
            with pytest.raises(WorkflowTransitionException) as exc:
                wf.confirm()
            assert 'Lead order confirmation is not enabled' in str(exc)

    @pytest.mark.parametrize('origin_state', ['new'])
    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system'])
    def test_workflow_confirm_without_availability_project_config_with_none(
        self, instance_obj, web_request, session, roles, role_name, now_utc, origin_state
    ):
        """Test LeadOrder workflow confirm transition without providing availability."""
        leadorder, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        leadorder.actual_order_price = 0
        # Remove the need for availability to be provided for a confirmed lead order
        project = leadorder.project
        project.leadorder_confirmation_fields = None

        wf.confirm()
        assert leadorder.state == 'received'

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
                'mobile': '+4917635573242',
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
                value = {
                    'type': 'Point',
                    'coordinates': [value[1], value[0]]
                }
                assert coordinates == value
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
        # TODO: improve this with requirement items, for now disable it
        leadorder.requirement_items = []
        session.flush()

        new_requirements = {}
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.edit_requirements(fields=new_requirements)

        assert 'Field number_required_assets is required for this transition' in str(excinfo)

        new_requirements['number_required_assets'] = 20
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.edit_requirements(fields=new_requirements)

        assert 'Field requirements is required for this transition' in str(excinfo)

        new_requirements['requirements'] = 'New requirements for this order!'
        new_requirements['number_required_assets'] = 25
        wf.edit_requirements(fields=new_requirements)
        session.flush()

        assert leadorder.state == origin_state
        assert leadorder.state_history[-1]['transition'] == 'edit_requirements'
        for key, value in new_requirements.items():
            assert getattr(leadorder, key) == value

    @pytest.mark.parametrize('origin_state', ['received'])
    @pytest.mark.parametrize(
        'role_name', ['pm', 'customer', 'bizdev', 'support', 'tech', 'product', 'system']
    )
    def test_workflow_remove_confirmation(
        self, instance_obj, web_request, session, roles, role_name, now_utc, origin_state
    ):
        """Test LeadOrder workflow remove confirmation transition."""
        leadorder, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        message = 'Remove lead order confirmation!'
        wf.remove_confirmation(message=message)
        session.flush()

        assert leadorder.state == 'new'
        assert leadorder.state_history[-1]['transition'] == 'remove_confirmation'
        assert leadorder.state_history[-1]['message'] == message
        assert leadorder.actual_order_price == 0

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
