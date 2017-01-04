"""Import and sync Knack Job to Leica Job."""
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica import logger
from briefy.leica.models import Comment
from briefy.leica.models import Assignment
from briefy.leica.models import OrderLocation
from briefy.leica.models import Order
from briefy.leica.models import Pool
from briefy.leica.models import Project
from briefy.leica.vocabularies import OrderInputSource as ISource
from briefy.leica.sync import PLACEHOLDERS
from briefy.leica.sync import ModelSync
from briefy.leica.sync.location import create_location_dict
from collections import OrderedDict
from datetime import datetime

import pytz
import uuid


# Field 'approval_status' on Knack.
# (Actually maps to several states on JobOrder and associated JobAssignments)
job_status_list = [
    ('Pending', 'pending'),
    ('Published', 'published'),
    ('Scheduled', 'scheduled'),
    ('Assigned', 'assigned'),
    ('Cancelled ', 'cancelled'),
    ('Awaiting Assets', 'awaiting_assets'),
    ('Approved', 'approved'),
    ('Completed', 'completed'),
    ('Refused', 'refused'),
    ('In QA', 'in_qa'),
]

job_status_mapping = OrderedDict(job_status_list)


def _status_after_or_equal(status_to_check, reference_status):
    for knack_name, name in job_status_list:
        if name == status_to_check:
            return True
        elif name == reference_status:
            return False


def first(seq):
    """Return the first element of a sequence or None if it is empty."""
    if not seq:
        return None
    return next(iter(seq))


isource_mapping = {item.label: item.value for item in ISource.__members__.values()}
category_mapping = {item.label: item.value for item in CategoryChoices.__members__.values()}


def _build_date(dt, minimal=None):
    """Return a safe str representation for a datetime.

    Given a valid datetime, or None and a valid minimal datetime,
    returns a valid str representation for it in i soformat-
    or the empty string.

    """
    if not dt and minimal:
        dt = minimal
    if dt:
        return dt.isoformat()
    return ''


def _get_identifier(kobj, field, default='Unknown'):
    """Retrieve the display name of given Knack relationship field."""
    attr = getattr(kobj, field, [])
    if not attr:
        return default
    return attr[0].get('identifier', default)


def add_order_history(session, obj, kobj):
    """Add state_history and state information to the Order."""
    history = []

    # create 'received' status

    person = _get_identifier(kobj, 'input_person', default='Briefy')
    history.append({
        'date': _build_date(kobj.input_date),
        'message': 'Created by {} on Knack database'.format(person),
        'actor': 'g:system',
        'transition': '',
        'from': '',
        'to': 'created'
    })
    # last_date = kobj.input_date

    history.append({
        'date': _build_date(kobj.input_date),
        'message': 'Automatic transition to received',
        'actor': 'g:system',
        'transition': 'submit',
        'from': 'created',
        'to': 'received'
    })
    last_date = kobj.input_date

    # check for 'assigned' status
    if kobj.assignment_date:
        person = _get_identifier(kobj, 'scouting_manager', default='Unknown')
        history.append({
            'date': _build_date(kobj.assignment_date, last_date),
            'message': "Photographer assigned by '{}' on the Knack database".format(person),
            'actor': 'g:system',
            'transition': 'assign',
            'from': 'received',
            'to': 'assigned'
        })
        last_date = kobj.assignment_date
    # check for 'scheduled' status
    if kobj.scheduled_shoot_date_time:
        date = kobj.scheduled_shoot_date_time
        if date in (kobj.availability_1, kobj.availability_2):
            person = _get_identifier(kobj, 'responsible_photographer', default='Photographer')
        else:
            person = 'Briefy'
        extra_message = ''
        if kobj.rescheduled:
            extra_message += (
                '''\nThis job was re-schedulled and may have been re-assigned/shot'''
                '''again. The old platform could not save this informaton. This transition'''
                '''refers to the last valid scheduling'''
            )
        history.append({
            'date': _build_date(date, last_date),
            'message': "Scheduled by '{}' on the Knack database".format(person) + extra_message,
            'actor': 'g:system',  # TODO: we could fetch the professional using Rosetta if needed.
            'transition': 'schedule',
            'from': history[-1]['to'],
            'to': 'scheduled'
        })
        last_date = date

    # check for 'in_qa' status
    if kobj.submission_date:
        date = kobj.submission_date
        person = _get_identifier(kobj, 'responsible_photographer', default='Photographer')
        history.append({
            'date': _build_date(date, last_date),
            'message': "Submited by '{}' on the Knack database".format(person),
            'actor': 'g:system',
            'transition': 'start_qa',
            'from': history[-1]['to'],
            'to': 'in_qa'
        })
        last_date = date

    # check for 'approved' status
    if kobj.client_delivery_link.url:
        date = kobj.last_approval_date or last_date
        person = _get_identifier(kobj, 'qa_manager', default='g:briefy_qa')
        history.append({
            'date': _build_date(date, last_date),
            'message': "Approved by '{}' on the Knack database".format(person),
            'actor': 'g:briefy_qa',
            'transition': 'approve',
            'from': history[-1]['to'],
            'to': 'in_qa'
        })
        last_date = date

    # check for 'cancelled' status
    if first(kobj.approval_status) == 'Cancelled':
        date = kobj.last_approval_date or last_date
        history.append({
            'date': _build_date(date, last_date),
            'message': 'Job cancelled on the Knack database by unknown actor',
            'actor': 'g:system',
            'transition': 'cancel',
            'from': history[-1]['to'],
            'to': 'cancelled'
        })
        last_date = date

    # check for 'refused' status
    if first(kobj.approval_status) == 'Refused':
        date = kobj.delivery_date_to_client or last_date
        history.append({
            'date': _build_date(date, last_date),
            'message': 'Job refused by client',
            'actor': 'g:system',
            'transition': 'refuse',
            'from': history[-1]['to'],
            'to': 'refused'
        })
        last_date = date

    obj.state_history = history
    obj.state = history[-1]['to']
    session.add(obj)
    model = obj.__class__.__name__
    logger.debug('{model} imported with state: {state}'.format(model=model, state=obj.state))


<<<<<<< Updated upstream
def add_assignment_history(session, obj, kobj):
=======
def add_assignment_history(session, obj, kobj, professional=None):
>>>>>>> Stashed changes
    """Add state_history and state information to the Assigment."""
    history = []

    # Check for 'created' status

    person = _get_identifier(kobj, 'input_person', default='Briefy')
    history.append({
        'date': _build_date(kobj.input_date),
        'message': 'Created by {} on Knack database'.format(person),
        'actor': 'g:system',
        'transition': '',
        'from': '',
        'to': 'created'
    })
    last_date = kobj.input_date
    # Check for 'validation' status
    # TODO - Current 'JobWorkflow' is incorrect-  validations should be after photo submssion, not
    # after creation
    # currently (commit d103c5b399)
    # the transition states go roughly:
    # created->validation->pending->assign->scheduled->awaiting_assets->in_qa
    # when the only thing that makes sense is:
    # created->pending->assign->scheduled->awaiting_assets->validation->in_qa

    # Except if we need an extra step of human validation for the metadata-  but
    # then we need an extra state.
    # Check for 'pending' status
    if _status_after_or_equal(first(kobj.approval_status), 'Pending'):
        history.append({
            'date': _build_date(kobj.input_date),
            'message': 'Transitioned to pending',
            'actor': 'g:system',
            'transition': 'make_ready',
            'from': 'created',
            'to': 'pending'
        })

    # Check for 'published' status
    if _get_identifier(kobj, 'scouting_manager').lower().strip() == 'job pool':
        history.append({
            'date': _build_date(kobj.input_date),
            'message': 'Job sent to job pool',
            'actor': 'g:system',
            'transition': 'publish',
            'from': 'pending',
            'to': 'published'
        })
    # Check for 'assigned' status

    if kobj.assignment_date:
        person = _get_identifier(kobj, 'scouting_manager', default='Unknown')

        # Back to assigned:
        history.append({
            'date': _build_date(kobj.assignment_date, kobj.input_date),
            'message': "Photographer assigned by '{}' on the Knack database".format(person),
            'actor': 'g:system',
            'transition': 'assign' if history[-1]['to'] == 'pending' else 'self_assign',
            'from': history[-1]['to'],
            'to': 'assigned'
        })
        last_date = kobj.assignment_date

    #  Check for 'scheduled' status
    if kobj.scheduled_shoot_date_time:
        date = kobj.scheduled_shoot_date_time
        if date in (kobj.availability_1, kobj.availability_2):
            person = _get_identifier(kobj, 'responsible_photographer', default='Photographer')
        else:
            person = 'Briefy'

        history.append({
            'date': _build_date(date, last_date),
            'message': "Scheduled by '{}' on the Knack database".format(person),
            'actor': 'g:system',
            'transition': 'schedule',
            'from': history[-1]['to'],
            'to': 'scheduled'
        })
        last_date = date

    #  Check for 'awaiting_assets' status
    dt = kobj.scheduled_shoot_date_time
    if dt and datetime.now(tz=pytz.UTC) > dt:
        history.append({
            'date': _build_date(kobj.scheduled_shoot_date_time, last_date),
            'message': 'Waiting for asset upload (from data on Knack)',
            'actor': 'g:system',
            'transition': 'ready_for_upload',
            'from': 'scheduled',
            'to': 'awaiting_assets',
        })
        last_date = kobj.scheduled_shoot_date_time

    # Check for Validation status: # TODO currently broken on the workflow.
    if kobj.submission_date:
        person = _get_identifier(kobj, 'responsible_photographer', default='Photographer')

        history.append({
            'date': _build_date(kobj.submission_date, last_date),
            'message': "Submited by '{}' (from data on Knack)".format(person),
            'actor': 'g:system',
            'transition': 'upload',
            'from': 'awaiting_assets',
            'to': 'validation',
        })
        last_date = kobj.submission_date

    # Check for 'in_qa' status
    if kobj.submission_date:
        date = kobj.last_approval_date or kobj.submission_date
        history.append({
            'date': _build_date(date, last_date),
            'message': "AUtomatic validation skipped (from data on Knack)",
            'actor': 'g:system',
            'transition': 'validate',
            'from': 'validation',
            'to': 'in_qa',  # Note: can't know about intermediary non-validated sets
        })
        last_date = date

    # Check for 'approved' status
    if kobj.approval_status and first(kobj.approval_status).lower() == 'approved':
        person = _get_identifier(kobj, 'qa_manager', default='g:briefy_qa')

        date = kobj.last_approval_date or kobj.submission_date
        history.append({
            'date': _build_date(kobj.submission_date, last_date),
            'message': "Approved by '{}'".format(person),
            'actor': 'g:briefy_qa',
            'transition': 'approve',
            'from': 'in_qa',
            'to': 'approved',
        })
        last_date = date

    # Check for 'completed' status # ERROR: 'completed' status should be on JobOrder
    # Check for 'edit' status # This can 't be reliably retrieved from Knack fields
    # Check for 'cancelled' status
    if kobj.approval_status and first(kobj.approval_status).lower() == 'cancelled':
        date = kobj.last_approval_date or kobj.submission_date
        history.append({
            'date': _build_date(kobj.submission_date, last_date),
            'message': "Cancelled by <unknown>".format(person),
            'actor': 'g:system',
            'transition': 'cancel',
            'from': history[-1]['to'],
            'to': 'cancelled',
        })
    # Check for 'refused' status
    if kobj.approval_status and kobj.approval_status.pop().lower() == 'refused':
        date = kobj.last_approval_date or kobj.submission_date
        project = _get_identifier(kobj, 'customer')
        history.append({
            'date': _build_date(kobj.submission_date, last_date),
            'message': "Set of photos refused by client from project '{}'".format(project),
            'actor': 'g:system',
            'transition': 'refuse',
            'from': 'approved',
            'to': 'refused',
        })

    obj.state_history = history
    obj.state = history[-1]['to']
    session.add(obj)
    model = obj.__class__.__name__
    logger.debug('{model} imported with state: {state}'.format(model=model, state=obj.state))


class JobSync(ModelSync):
    """Syncronize Job: Order, OrderLocation and Assignment."""

    model = Order
    knack_model_name = 'Job'
    knack_parent_model = 'Project'
    parent_model = Project
    bulk_insert = False

    def get_slug(self, job_id: str, assignment: int = 0):
        """Create new slug for Order and Assignment."""
        # TODO: check jobs in knack with internal_job_id == 0
        job_id = job_id.replace('C', '')
        job_id = '{job_id:04d}'.format(job_id=int(job_id.replace('-', '')[-4:]))
        slug = '1701-PS{0}-{1}'.format(job_id[0], job_id[1:4])
        if assignment:
            slug = '{slug}_{assignment:02d}'.format(slug=slug, assignment=assignment)

        return slug

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for customer object."""
        order_payload = super().get_payload(kobj, briefy_id)
        project, kproject = self.get_parent(kobj, 'project')
        job_id = str(kobj.internal_job_id or kobj.job_id)

        order_payload.update(
            dict(
                title=kobj.job_name,
                description='',
                category=category_mapping.get(str(kobj.category), 'undefined'),
                project_id=project.id,
                customer_id=project.customer.id,
                price=self.parse_decimal(kobj.set_price),
                customer_order_id=kobj.job_id,
                slug=self.get_slug(job_id),
                job_id=job_id,
                external_id=kobj.id,
                requirements=kobj.client_specific_requirement,
                number_required_assets=kobj.number_of_photos,
                source=isource_mapping.get(str(kobj.input_source), 'briefy'),
            )
        )
        return order_payload

    def add_location(self, obj, kobj):
        """Add Job location to the Order."""
        payload = create_location_dict('job_location', kobj)
        if payload:
            country = payload['country']
            payload['order_id'] = obj.id
            payload.update(
                id=uuid.uuid4(),
                mobile=self.parse_phonenumber(kobj, 'contact_number_1', country),
                additional_phone=self.parse_phonenumber(kobj, 'contact_number_2', country),
                email=kobj.contact_email.email or PLACEHOLDERS['email'],
                first_name=kobj.contact_person.first or PLACEHOLDERS['first_name'],
                last_name=kobj.contact_person.last or PLACEHOLDERS['last_name'],
            )
            try:
                location = OrderLocation(**payload)
                self.session.add(location)
                obj.location = location
            except Exception as exc:
                print(exc)
        else:
            msg = 'Failure to create location for Job: {job}, no location found.'
            logger.info(msg.format(job=obj.customer_order_id))

    def add_comment(self, obj, kobj):
        """Add Project Manager comment to the Order."""
        project_manager = obj.project.project_manager if obj.project.project_manager else None
        payload = dict(
            id=uuid.uuid4(),
            entity_id=obj.id,
            entity_type=obj.__tablename__,
            author_id=project_manager,
            content=kobj.project_manager_comment
        )
        session = self.session
        session.add(Comment(**payload))

    def add_assigment_comments(self, obj, kobj):
        """Import assigment comments."""
        # TODO: internal comment, photographer comment, quality assurance feedback
        pass

    def add_assigment(self, obj, kobj):
        """Add a related assign object."""
<<<<<<< Updated upstream
        # TODO: import comments

        payable = True
        if kobj.approval_status == {'Cancelled'}:
            payable = False

        professional_id = self.get_user(kobj, 'responsible_photographer')
        job_id = str(kobj.internal_job_id or kobj.job_id)
        kpool_id = kobj.job_pool[0]['id'] if kobj.job_pool else None
        job_pool = Pool.query().filter_by(external_id=kpool_id).one_or_none()
        if kpool_id and not job_pool:
            print('Knack Poll ID: {0} do not found in leica.'.format(kpool_id))
=======
        # TODO: dates should be created as workflow history transitions
        # assignment_date = kobj.assignment_date
        # add comments
        professional_id = self.get_user(kobj, 'responsible_photographer')
        _, professional_name = _get_identifier(kobj, 'responsible_photographer')
        payable = kobj.approval_status != {'Cancelled'}
>>>>>>> Stashed changes
        payload = dict(
            id=uuid.uuid4(),
            order_id=obj.id,
            pool=job_pool,
            slug=self.get_slug(job_id, assignment=1),
            professional_id=professional_id,
            payout_value=self.parse_decimal(kobj.photographer_payout),
            payout_currency=kobj.currency_payout or 'EUR',
            additional_compensation=self.parse_decimal(kobj.additional_compensation),
            payable=payable,
            submission_path=str(kobj.photo_submission_link),
            travel_expenses=self.parse_decimal(kobj.travel_expenses),
        )
        assignment = Assignment(**payload)
        self.session.add(assignment)
        logger.debug('Assignment added: {id}'.format(id=assignment.id))

        if professional_id:
            self.update_local_roles(assignment, [professional_id], 'professional_user')

        # qa manager context roles
        qa_manager_roles = self.get_local_roles(kobj, 'qa_manager')
        self.update_local_roles(assignment, qa_manager_roles, 'qa_manager')

        # scout manager context roles
        scout_manager_roles = self.get_local_roles(kobj, 'scouting_manager')
        self.update_local_roles(assignment, scout_manager_roles, 'scout_manager')

        # project manager context roles
        pm_roles_roles = [role.user_id for role in obj.project.local_roles
                          if role.role_name.value == 'project_manager']
        self.update_local_roles(assignment, pm_roles_roles, 'project_manager')

        # update assignment state history
        add_assignment_history(self.session, assignment, kobj,
                               professional=(professional_id, professional_name))

    def add(self, kobj, briefy_id):
        """Add new Job to database."""
        obj = super().add(kobj, briefy_id)
        project = obj.project

        # customer context roles
        customer_roles = [role.user_id for role in project.local_roles
                          if role.role_name.value == 'customer_user']
        self.update_local_roles(obj, customer_roles, 'customer_user')

        # scout manager context roles
        scout_manager_roles = self.get_local_roles(kobj, 'scouting_manager')
        self.update_local_roles(obj, scout_manager_roles, 'scout_manager')

        # project manager context roles
        pm_roles_roles = [role.user_id for role in project.local_roles
                          if role.role_name.value == 'project_manager']
        self.update_local_roles(obj, pm_roles_roles, 'project_manager')

        add_order_history(self.session, obj, kobj)
        self.add_location(obj, kobj)
        self.add_comment(obj, kobj)
        self.add_assigment(obj, kobj)
        logger.debug('Additional data imported for this order: History, Location, Comment.')
        return obj
