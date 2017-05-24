"""Test Order database model."""
from briefy.common.workflow.exceptions import WorkflowTransitionException
from briefy.leica import models
from briefy.leica.events.assignment import AssignmentCreatedEvent
from briefy.leica.events.order import OrderCreatedEvent
from briefy.leica.subscribers.assignment import assignment_created_handler
from briefy.leica.subscribers.order import order_created_handler
from conftest import BaseModelTest
from datetime import timedelta

import pytest
import pytz
import uuid


@pytest.mark.usefixtures('create_dependencies')
class TestOrderModel(BaseModelTest):
    """Test Order."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json')
    ]
    file_path = 'data/orders.json'
    model = models.Order
    initial_wf_state = 'received'
    number_of_wf_transtions = 1

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
        """Test workflow submit after order creation."""
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            'created',
        )

        # manually execute the order created handler
        event = OrderCreatedEvent(order, web_request)
        order_created_handler(event)
        event()
        session.flush()

        assert order.assignment is None
        assert 'submit' not in wf.transitions
        assert order.state == 'received'
        assert order.state_history[-1]['transition'] == 'submit'
        project = order.project
        assert order.price == project.price
        assert order.price_currency == project.price_currency
        assert order.asset_types == project.asset_types[:1]

        received_transitions = (
            'cancel', 'set_availability', 'edit_location', 'edit_requirements',
        )
        for transition in received_transitions:
            assert transition in wf.transitions

        assignment = order.assignments[-1]
        self.notify_assigment_created(assignment, request, session)
        assert assignment.state == 'pending'
        assert assignment.state_history[-1]['transition'] == 'submit'
        assert assignment.asset_types == order.asset_types
        self.delete_assigment_created(assignment, session)

    @pytest.mark.parametrize('file_path', ['data/order_locations.json'])
    @pytest.mark.parametrize('position', [0])
    @pytest.mark.parametrize('origin_state', ['received', 'assigned', 'scheduled'])
    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system'])
    def test_workflow_edit_location(
        self, instance_obj, session, web_request, roles, role_name, origin_state, obj_payload_other
    ):
        """Test Order workflow edit_location transition."""
        location_payload = obj_payload_other
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.edit_location()
            assert 'Field location is required for this transition' in str(excinfo)

        # delete previous existing order location before adding a new one
        if order.location:
            session.delete(order.location)
            session.flush()

        # add a new location to the order
        location_payload['order_id'] = order.id
        location_payload['id'] = str(uuid.uuid4())
        location = models.OrderLocation(**location_payload)
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

        assert order.state == origin_state
        assert order.state_history[-1]['transition'] == 'edit_location'

        location_payload = new_location_payload['location']
        for key, value in location_payload.items():
            if key == 'info':
                info_payload = location_payload['info']
                for ikey, ivalue in info_payload.items():
                    assert order.location.info[ikey] == ivalue
            elif key == 'coordinates':
                coordinates = getattr(order.location, key)
                value = {
                    'type': 'Point',
                    'coordinates': [value[1], value[0]]
                }
                assert coordinates == value
            else:
                assert getattr(order.location, key) == value

    @pytest.mark.parametrize('origin_state', ['received', 'assigned', 'scheduled'])
    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system'])
    def test_workflow_edit_requirements(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test Order workflow edit_requirements transition."""
        order, wf, request = self.prepare_obj_wf(
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

        assert order.state == origin_state
        assert order.state_history[-1]['transition'] == 'edit_requirements'
        for key, value in new_requirements.items():
            assert getattr(order, key) == value

    @pytest.mark.parametrize('origin_state', ['received', 'assigned'])
    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system'])
    def test_workflow_set_availability(
        self, instance_obj, web_request, session, roles, role_name, now_utc, origin_state
    ):
        """Test Order workflow set_availability transition."""
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )
        now_utc = now_utc.astimezone(pytz.timezone(order.timezone))

        new_availability = {}
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.set_availability(fields=new_availability)

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
                wf.set_availability(fields=new_availability)

            assert 'Both availability dates must be at least 7 days from now' in str(excinfo)

        availability_1 = now_utc + timedelta(8)
        availability_2 = now_utc + timedelta(10)

        new_availability['availability'] = [
            availability_1.isoformat(),
            availability_2.isoformat()
        ]
        wf.set_availability(fields=new_availability)
        session.flush()
        assert order.state == origin_state
        assert order.state_history[-1]['transition'] == 'set_availability'
        for key, value in new_availability.items():
            assert getattr(order, key) == value

        # should work also with normal python datetime instances
        new_availability['availability'] = [
            availability_1,
            availability_2,
        ]
        wf.set_availability(fields=new_availability)
        session.flush()

        assert order.state == origin_state
        for key, value in new_availability.items():
            assert getattr(order, key)[0] == value[0].isoformat()
            assert getattr(order, key)[1] == value[1].isoformat()

    @pytest.mark.parametrize('origin_state', ['assigned', 'scheduled'])
    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system'])
    def test_workflow_remove_availability(
        self, instance_obj, web_request, session, roles, role_name, now_utc, origin_state
    ):
        """Test Order workflow remove_availability transition."""
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state
        )

        availability_1 = now_utc + timedelta(10)
        availability_2 = now_utc + timedelta(11)
        new_availability = [
            availability_1.isoformat(),
            availability_2.isoformat()
        ]
        order.availability = new_availability
        session.flush()

        old_assignment = order.assignments[-1]
        old_assignment, ass_wf, request = self.prepare_obj_wf(
            old_assignment,
            web_request,
            roles[role_name],
            origin_state,
        )
        message = 'Remove availability!'
        wf.remove_availability(message=message)
        session.flush()

        new_assignment = order.assignments[-1]
        self.notify_assigment_created(new_assignment, request, session)

        assert order.state == 'received'
        assert order.state_history[-1]['transition'] == 'remove_availability'
        assert order.state_history[-1]['message'] == message
        assert len(order.availability) == 0
        assert old_assignment.state == 'cancelled'
        assert old_assignment.state_history[-1]['transition'] == 'cancel'
        assert new_assignment.state == 'pending'
        assert new_assignment.state_history[-1]['transition'] == 'submit'
        self.delete_assigment_created(new_assignment, session)

    @pytest.mark.parametrize('role_name', ['pm', 'scout', 'system'])
    def test_workflow_assign(self, instance_obj, web_request, session, roles, role_name):
        """Test Order workflow assign transition."""
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            'received',
        )
        scout_manager = {}
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.assign(fields=scout_manager)

        assert 'Field scout_manager is required for this transition' in str(excinfo)

        scout_manager = {'scout_manager': uuid.uuid4()}
        wf.assign(fields=scout_manager)
        session.flush()

        assert order.state == 'assigned'
        assert order.state_history[-1]['transition'] == 'assign'

        for key, value in scout_manager.items():
            assert getattr(order, key) == value

    @pytest.mark.parametrize('origin_state', ['assigned', 'scheduled'])
    @pytest.mark.parametrize('role_name', ['pm', 'system'])
    def test_workflow_unassign(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test Order workflow unassign transition."""
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state,
        )
        assignment = order.assignments[-1]
        assignment, ass_wf, request = self.prepare_obj_wf(
            assignment,
            web_request,
            roles[role_name],
            origin_state,
        )
        assignment.workflow.context = roles[role_name]
        assignment.submission_path = 'http://submision.link'

        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.unassign()
        assert 'assignment already have a submission' in str(excinfo)

        assignment.submission_path = None
        message = 'Un-assign Order!'
        wf.unassign(message=message)
        session.flush()

        new_assignment = order.assignments[-1]
        self.notify_assigment_created(new_assignment, request, session)

        assert order.state == 'received'
        assert order.state_history[-1]['transition'] == 'unassign'
        assert order.comments[0].content == message
        assert new_assignment.state == 'pending'
        assert new_assignment.state_history[-1]['transition'] == 'submit'
        self.delete_assigment_created(new_assignment, session)

    @pytest.mark.parametrize('origin_state', ['received', 'assigned'])
    @pytest.mark.parametrize('role_name', ['pm', 'scout', 'system'])
    def test_workflow_schedule(
        self, instance_obj, web_request, session, roles, role_name, origin_state, now_utc
    ):
        """Test Order workflow schedule transition."""
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state,
        )

        assignment = order.assignments[-1]
        assignment, ass_wf, request = self.prepare_obj_wf(
            assignment,
            web_request,
            roles[role_name],
            'assigned',
        )
        assignment.scheduled_datetime = now_utc

        message = 'Order scheduled'
        wf.schedule(message=message, fields={'scheduled_datetime': now_utc})
        session.flush()

        assert order.state == 'scheduled'
        assert order.state_history[-1]['transition'] == 'schedule'
        assert order.state_history[-1]['message'] == message
        assert order.scheduled_datetime is not None
        assert order.scheduled_datetime == assignment.scheduled_datetime

    @pytest.mark.parametrize('origin_state', ['received', 'assigned', 'scheduled'])
    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system'])
    def test_workflow_cancel(
        self, instance_obj, web_request, session, roles, role_name, origin_state
    ):
        """Test Order workflow cancel transition."""
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state,
        )

        assignment = order.assignments[-1]
        assignment, ass_wf, request = self.prepare_obj_wf(
            assignment,
            web_request,
            roles[role_name],
            'pending'
        )

        message = 'Order cancelled'
        order.workflow.cancel(message=message)
        session.flush()

        assert order.state == 'cancelled'
        assert order.state_history[-1]['transition'] == 'cancel'
        assert order.state_history[-1]['message'] == message
        assert order.comments[0].content == message
        assert assignment.state == 'cancelled'
        assert assignment.state_history[-1]['transition'] == 'cancel'
        assert assignment.payout_value == 0
        assert assignment.scheduled_datetime is None

    @pytest.mark.parametrize('role_name', ['qa', 'system'])
    def test_workflow_start_qa(
        self, instance_obj, web_request, session, roles, role_name
    ):
        """Test Order workflow start_qa transition."""
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            'scheduled',
        )

        message = 'Order moved to QA'
        order.workflow.start_qa(message=message)
        session.flush()

        assert order.state == 'in_qa'
        assert order.state_history[-1]['transition'] == 'start_qa'
        assert order.state_history[-1]['message'] == message

    @pytest.mark.parametrize('role_name', ['qa', 'system'])
    def test_workflow_deliver(
        self, instance_obj, web_request, session, roles, role_name
    ):
        """Test Order workflow deliver transition."""
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            'in_qa',
        )

        delivery = {}
        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.deliver(fields=delivery)
        assert 'Field delivery is required for this transition' in str(excinfo)

        delivery = {
            'delivery': {
                'gdrive': 'http://some.gdrive.link',
                'archive': 'http://some.archive.link',
            }
        }
        message = 'Order Delivered!'
        order.workflow.deliver(message=message, fields=delivery)
        session.flush()

        assert order.state == 'delivered'
        assert order.state_history[-1]['transition'] == 'deliver'
        assert order.state_history[-1]['message'] == message
        assert order.delivery == delivery['delivery']

    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system'])
    def test_workflow_refuse(
        self, instance_obj, web_request, session, roles, role_name
    ):
        """Test Order workflow refuse transition."""
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            'delivered',
        )

        assignment = order.assignments[-1]
        assignment, ass_wf, request = self.prepare_obj_wf(
            assignment,
            web_request,
            roles[role_name],
            'approved'
        )

        message = 'Order refused!'
        order.workflow.refuse(message=message)
        session.flush()

        assert order.state == 'refused'
        assert order.state_history[-1]['transition'] == 'refuse'
        assert order.state_history[-1]['message'] == message
        assert assignment.state == 'refused'
        assert assignment.state_history[-1]['transition'] == 'refuse'
        assert assignment.state_history[-1]['message'] == message

    @pytest.mark.parametrize('ass_origin_state', ['refused', 'approved', ])
    @pytest.mark.parametrize('origin_state', ['delivered', 'refused', ])
    @pytest.mark.parametrize('role_name', ['pm', 'customer', 'system'])
    def test_workflow_accept(
        self, instance_obj, web_request, session, roles, role_name, origin_state, ass_origin_state
    ):
        """Test Order workflow accept transition."""
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state,
        )

        for assignment in order.assignments:
            self.prepare_obj_wf(
                assignment,
                web_request,
                roles[role_name],
                ass_origin_state
            )

        message = 'Order accepted!'
        order.workflow.accept(message=message)
        session.flush()

        assert order.state == 'accepted'
        assert order.state_history[-1]['transition'] == 'accept'
        assert order.state_history[-1]['message'] == message
        assert order.comments[0].content == message

        ass_message = 'Assignment complete by Order accept transition.'
        for assignment in order.assignments:
            assert assignment.state == 'completed'
            assert assignment.state_history[-1]['transition'] == 'complete'
            assert assignment.state_history[-1]['message'] == ass_message

    @pytest.mark.parametrize('role_name', ['pm', 'finance', 'system'])
    def test_workflow_perm_refuse(
        self, instance_obj, web_request, session, roles, role_name
    ):
        """Test Order workflow perm_refuse transition."""
        origin_state = 'refused'
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state,
        )

        assignment = order.assignments[-1]
        assignment, ass_wf, request = self.prepare_obj_wf(
            assignment,
            web_request,
            roles[role_name],
            origin_state
        )

        message = 'Order permanently refused!'
        order.workflow.perm_refuse(message=message)
        session.flush()

        assert order.state == 'perm_refused'
        assert order.state_history[-1]['transition'] == 'perm_refuse'
        assert order.state_history[-1]['message'] == message

        assert assignment.state == 'completed'
        assert assignment.state_history[-1]['transition'] == 'complete'
        assert assignment.state_history[-1]['message'] is None

    @pytest.mark.parametrize('origin_state', ['in_qa', 'refused', ])
    @pytest.mark.parametrize('ass_origin_state', ['in_qa', 'refused', 'approved', ])
    @pytest.mark.parametrize('role_name', ['pm', 'qa', 'system'])
    def test_workflow_newshoot(
        self, instance_obj, web_request, session, roles, role_name, origin_state, ass_origin_state
    ):
        """Test Order workflow newshoot transition."""
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state,
        )

        old_assignment = order.assignments[-1]
        old_assignment, ass_wf, request = self.prepare_obj_wf(
            old_assignment,
            web_request,
            roles[role_name],
            ass_origin_state
        )

        fields = {}
        message = 'Order newshoot!'
        with pytest.raises(WorkflowTransitionException) as excinfo:
            order.workflow.new_shoot(message=message, fields=fields)
        assert 'Field payout_value is required for this transition' in str(excinfo)

        fields['payout_value'] = 10000
        with pytest.raises(WorkflowTransitionException) as excinfo:
            order.workflow.new_shoot(message=message, fields=fields)
        assert 'Field travel_expenses is required for this transition' in str(excinfo)

        fields['travel_expenses'] = 1000
        order.workflow.new_shoot(message=message, fields=fields)
        session.flush()

        new_assignment = order.assignments[-1]
        self.notify_assigment_created(new_assignment, request, session)

        assert order.state == 'received'
        assert order.state_history[-1]['transition'] == 'new_shoot'
        assert order.state_history[-1]['message'] == message
        assert order.comments[0].content == message
        assert old_assignment.state == 'completed'
        assert old_assignment.state_history[-1]['transition'] == 'complete'
        assert old_assignment.travel_expenses == fields['travel_expenses']
        assert old_assignment.payout_value == fields['payout_value']
        assert new_assignment.state == 'pending'
        assert new_assignment.state_history[-1]['transition'] == 'submit'
        self.delete_assigment_created(new_assignment, session)

    @pytest.mark.parametrize('ass_origin_state', ['in_qa', 'refused', 'approved', ])
    @pytest.mark.parametrize('origin_state', ['in_qa', 'refused', ])
    @pytest.mark.parametrize('role_name', ['pm', 'qa', 'system'])
    def test_workflow_reshoot(
        self, instance_obj, web_request, session, roles, role_name, origin_state, ass_origin_state
    ):
        """Test Order workflow reshoot transition."""
        order, wf, request = self.prepare_obj_wf(
            instance_obj,
            web_request,
            roles[role_name],
            origin_state,
        )

        old_assignment = order.assignments[-1]
        old_assignment, ass_wf, request = self.prepare_obj_wf(
            old_assignment,
            web_request,
            roles[role_name],
            ass_origin_state
        )

        # make sure old assignment has a valid professional: Sebastiao Salgado
        old_assignment.professional_id = '23d94a43-3947-42fc-958c-09245ecca5f2'
        # save old assignment values do compare later
        old_assignment_travel_expenses = old_assignment.travel_expenses
        old_assignment_payout_value = old_assignment.payout_value

        fields = {}
        message = 'Order reshoot!'
        with pytest.raises(WorkflowTransitionException) as excinfo:
            order.workflow.reshoot(message=message, fields=fields)
        assert 'Field payout_value is required for this transition' in str(excinfo)

        fields['payout_value'] = 10000
        with pytest.raises(WorkflowTransitionException) as excinfo:
            order.workflow.reshoot(message=message, fields=fields)
        assert 'Field travel_expenses is required for this transition' in str(excinfo)

        fields['travel_expenses'] = 1000
        order.workflow.reshoot(message=message, fields=fields)
        session.flush()

        new_assignment = order.assignments[-1]
        self.notify_assigment_created(new_assignment, request, session)

        assert order.state == 'assigned'
        assert order.state_history[-1]['transition'] == 'reshoot'
        assert order.state_history[-1]['message'] == message
        assert order.comments[0].content == message
        assert old_assignment.state == 'completed'
        assert old_assignment.state_history[-1]['transition'] == 'complete'
        assert old_assignment.travel_expenses == fields['travel_expenses']
        assert old_assignment.payout_value == fields['payout_value']
        assert new_assignment.state == 'assigned'
        assert new_assignment.state_history[-1]['transition'] == 'assign'
        assert new_assignment.professional_id == old_assignment.professional_id
        assert new_assignment.payout_currency == old_assignment.payout_currency
        assert new_assignment.travel_expenses == old_assignment_travel_expenses
        assert new_assignment.payout_value == old_assignment_payout_value
