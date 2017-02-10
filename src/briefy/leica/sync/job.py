"""Import and sync Knack Job to Leica Job."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.leica import logger
from briefy.leica.config import FILES_BASE
from briefy.leica.models import Comment
from briefy.leica.models import Assignment
from briefy.leica.models import OrderLocation
from briefy.leica.models import Order
from briefy.leica.models import Pool
from briefy.leica.models import Project
from briefy.leica.vocabularies import OrderInputSource as ISource
from briefy.leica.sync import get_model_and_data
from briefy.leica.sync import PLACEHOLDERS
from briefy.leica.sync import ModelSync
from briefy.leica.sync import category_mapping
from briefy.leica.sync.job_comment import comment_format_first_line
from briefy.leica.sync.job_comment import parse_internal_comments
from briefy.leica.sync.job_wf_history import _build_date
from briefy.leica.sync.job_wf_history import add_assignment_history
from briefy.leica.sync.job_wf_history import add_order_history
from briefy.leica.sync.location import create_location_dict
from datetime import datetime
from pytz import utc
from pytz import timezone

import re
import uuid

isource_mapping = {item.label: item.value for item in ISource.__members__.values()}


def datetime_in_timezone(value: datetime, tz_name: str) -> datetime:
    """Process a datetime, in UTC and return it in the specified timezone."""
    tz = timezone(tz_name)
    # We will assume the original date was in UTC
    # So we need to remove UTC
    new_value = datetime(
        *[int(p) for p in value.strftime('%Y-%m-%d-%H-%M-%S').split('-')]
    )
    new_value = tz.localize(new_value)
    return new_value


class JobSync(ModelSync):
    """Syncronize Job: Order, OrderLocation and Assignment."""

    model = Order
    knack_model_name = 'Job'
    knack_parent_model = 'Project'
    parent_model = Project
    bulk_insert = False
    knack_version_model = None
    versions = {}

    def get_version_items(self):
        """Get all items for one knack model."""
        self.knack_version_model, items = get_model_and_data('JobVersion')
        versions = {}
        for item in items:
            if not item.job:
                continue
            id_ = item.job[0]['id']
            if id_ not in versions:
                versions[id_] = []
            versions[id_].append(item)
        self.versions = versions

    def updated_at(self, kobj):
        """Return updated_at value."""
        input_date = _build_date(kobj.input_date),
        updated_at = _build_date(kobj.updated_at)
        assignment_date = _build_date(kobj.assignment_date)
        submission_date = _build_date(kobj.submission_date)
        last_approval_date = _build_date(kobj.last_approval_date)
        last_photographer_update = _build_date(kobj.last_photographer_update)
        delivery_date_to_client = _build_date(kobj.delivery_date_to_client)

        updated_at = (
            updated_at or delivery_date_to_client or
            last_approval_date or last_photographer_update or
            submission_date or assignment_date or input_date
        )
        return updated_at

    def get_slug(self, job_id: str, assignment: int = 0):
        """Create new slug for Order and Assignment."""
        # TODO: check jobs in knack with internal_job_id == 0
        job_id = job_id.replace('C', '')
        job_id = job_id.replace('_', '')
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
        number_required_assets = kobj.number_of_photos or project.number_required_assets or 10
        category = kobj.category.pop() if kobj.category else 'undefined'
        category = 'Accommodation' if category == 'Accomodation' else category
        category = 'Portrait' if category == 'Portraits' else category
        timezone_name = kobj.timezone
        availability_1 = kobj.availability_1
        availability_2 = kobj.availability_2
        if availability_1 and availability_2:
            # First convert to local timezone and then get it in UTC
            availability_1 = datetime_in_timezone(availability_1, timezone_name)
            availability_1 = availability_1.astimezone(utc)
            availability_2 = datetime_in_timezone(availability_2, timezone_name)
            availability_2 = availability_2.astimezone(utc)
            availability = [
                availability_1.isoformat(),
                availability_2.isoformat()
            ]
        else:
            availability = None

        delivery_link_str = kobj.client_delivery_link.url
        delivery = dict()
        if delivery_link_str and delivery_link_str[:4] == 'sftp':
            delivery['sftp'] = delivery_link_str
        elif delivery_link_str:
            delivery['gdrive'] = delivery_link_str

        requirements = kobj.client_specific_requirement or None
        knack_input_source = self.choice_to_str(kobj.input_source)
        category = category_mapping.get(category, '') or project.category
        order_payload.update(
            dict(
                title=kobj.job_name,
                description='',
                created_at=_build_date(kobj.input_date),
                updated_at=self.updated_at(kobj),
                category=category,
                project_id=project.id,
                customer_id=project.customer.id,
                price=self.parse_decimal(kobj.set_price) or project.price,
                customer_order_id=kobj.job_id,
                slug=self.get_slug(job_id),
                delivery=delivery,
                job_id=job_id,
                availability=availability,
                external_id=kobj.id,
                price_currency=project.price_currency,
                requirements=requirements,
                number_required_assets=number_required_assets,
                source=isource_mapping.get(knack_input_source, 'briefy'),
            )
        )
        if order_payload.get('category') == 'undefined':
            logger.debug('Category undefined knack Job: {job_id}'.format(job_id=job_id))
        return order_payload

    def add_location(self, obj, kobj):
        """Add Job location to the Order."""
        payload = create_location_dict('job_location', kobj)
        if payload:
            country = payload['country']
            payload['order_id'] = obj.id
            contact = kobj.contact_person
            first_name = contact.first.strip() if isinstance(contact.first, str) else ''
            last_name = contact.last.strip() if isinstance(contact.last, str) else ''

            if first_name and not last_name:
                pieces = first_name.split(' ')
                last_name = pieces[-1] if len(pieces) > 1 else PLACEHOLDERS['last_name']
                first_name = ' '.join(pieces[:-1]) if len(pieces) > 1 else first_name

            if not first_name:
                first_name = PLACEHOLDERS['first_name']
            if not last_name:
                last_name = PLACEHOLDERS['last_name']

            payload.update(
                id=uuid.uuid4(),
                mobile=self.parse_phonenumber(kobj, 'contact_number_1', country),
                additional_phone=self.parse_phonenumber(kobj, 'contact_number_2', country),
                email=kobj.contact_email.email or PLACEHOLDERS['email'],
                first_name=first_name,
                last_name=last_name,
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

    def parse_machine_log(self, kobj):
        """Parse machine log on Knack object."""
        history = []
        pattern = """(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.[\d]*:([^ ]*)"""
        matches = re.findall(pattern, kobj.machine_log)
        for item in matches:
            data = datetime(*[int(i) for i in item[0:-1]], tzinfo=timezone.utc)
            action = item[-1]
            history.append({'data': data, 'action': action})
        return history

    def parse_comment(self, body: str) -> list:
        """Parse comment field and return a list of comments."""
        pattern = '\n([-]+)\n'
        comment = body
        comment = re.sub(pattern, '\n------------------------------\n', comment)
        pattern = '\n([_]+)\n'
        comment = re.sub(pattern, '\n------------------------------\n', comment)
        comments = comment.split('------------------------------\n')
        comments = [c for c in comments if c.strip()]
        comments.reverse()
        return comments

    def add_comment(self, obj, kobj):
        """Add Project Manager comment to the Order."""
        if kobj.project_manager_comment:
            project_manager = obj.project.project_manager if obj.project.project_manager else None
            comments_data = self.parse_comment(kobj.project_manager_comment)
            for content in comments_data:
                created_at, body = comment_format_first_line(datetime_utcnow(), content)
                payload = dict(
                    id=uuid.uuid4(),
                    entity_id=obj.id,
                    entity_type=obj.__class__.__name__,
                    author_id=project_manager,
                    content=body,
                    created_at=created_at,
                    updated_at=created_at,
                    author_role='project_manager',
                    to_role='customer_user',
                    internal=False,
                )
                session = self.session
                session.add(Comment(**payload))

        if kobj.client_feedback:
            customer_user = obj.project.customer_user or obj.project.project_manager
            comments_data = self.parse_comment(kobj.client_feedback)
            for content in comments_data:
                created_at, body = comment_format_first_line(datetime_utcnow(), content)
                payload = dict(
                    id=uuid.uuid4(),
                    entity_id=obj.id,
                    entity_type=obj.__class__.__name__,
                    author_id=customer_user,
                    content=body,
                    created_at=created_at,
                    updated_at=created_at,
                    author_role='customer_user',
                    to_role='project_manager',
                    internal=False,
                )
                session = self.session
                session.add(Comment(**payload))

    def add_internal_comments(self, obj, kobj):
        """Add Project Manager comment to the Order."""
        if kobj.internal_comments:
            comments_data = parse_internal_comments(obj, kobj)
            session = self.session
            for comment in comments_data:
                session.add(Comment(**comment))

    def parse_quality_assurance_feedback(self, kobj):
        """Quality assurance feedback can be parsed to a list of comments."""
        raw_comment = kobj.quality_assurance_feedback
        comment = raw_comment.replace(
            'This is an automatic feedback.\n',
            '------------------------------\nThis is an automatic feedback.\n'
        )
        comment = comment.replace(
            '\nThe images listed below do not meet our technical requirements:\n\nNext steps:',
            '\n\nNext steps:',
        )
        return self.parse_comment(comment)

    def add_assignment_comments(self, obj, kobj):
        """Import Assignment comments."""
        if kobj.note_from_pm:
            project_manager = obj.project.project_manager
            comments_data = self.parse_comment(kobj.note_from_pm)
            for content in comments_data:
                created_at, body = comment_format_first_line(datetime_utcnow(), content)
                author_role = 'project_manager'
                author_id = project_manager
                payload = dict(
                    id=uuid.uuid4(),
                    entity_id=obj.id,
                    entity_type=obj.__class__.__name__,
                    author_id=author_id,
                    content=body,
                    created_at=created_at,
                    author_role=author_role,
                    to_role='professional_user',
                    internal=False,
                )
                session = self.session
                session.add(Comment(**payload))
        if kobj.photographers_comment and obj.professional_id:
            comments_data = self.parse_comment(kobj.photographers_comment)
            for content in comments_data:
                created_at, body = comment_format_first_line(datetime_utcnow(), content)
                payload = dict(
                    id=uuid.uuid4(),
                    entity_id=obj.id,
                    entity_type=obj.__class__.__name__,
                    author_id=obj.professional_id,
                    content=body,
                    created_at=created_at,
                    author_role='professional_user',
                    to_role='qa_manager',
                    internal=False,
                )
                session = self.session
                session.add(Comment(**payload))

        if kobj.quality_assurance_feedback:
            # history = self.parse_machine_log(kobj)
            # failed = [entry for entry in history if entry['action'] == 'invalidate']
            qa_manager = obj.qa_manager or obj.project.project_manager
            ms_laure = SystemUser.id
            comments_data = self.parse_quality_assurance_feedback(kobj)
            for content in comments_data:
                created_at, body = comment_format_first_line(datetime_utcnow(), content)
                author_role = 'qa_manager'
                author_id = qa_manager
                if content.startswith('This is an automatic'):
                    author_role = 'system'
                    author_id = ms_laure
                payload = dict(
                    id=uuid.uuid4(),
                    entity_id=obj.id,
                    entity_type=obj.__class__.__name__,
                    author_id=author_id,
                    content=body,
                    created_at=created_at,
                    author_role=author_role,
                    to_role='professional_user',
                    internal=False,
                )
                session = self.session
                session.add(Comment(**payload))

    def add_assignment(self, obj, kobj):
        """Add a related assign object."""
        payable = True
        if kobj.approval_status == {'Cancelled'}:
            payable = False
        professional_id = self.get_user(kobj, 'responsible_photographer')
        job_id = str(kobj.internal_job_id or kobj.job_id)
        kpool_id = kobj.job_pool[0]['id'] if kobj.job_pool else None
        job_pool = Pool.query().filter_by(external_id=kpool_id).one_or_none()
        if kpool_id and not job_pool:
            print('Knack Poll ID: {0} do not found in leica.'.format(kpool_id))

        release = kobj.signed_releases_contract
        if release:
            release = '{0}/files/order/{1}/release/{2}'.format(
                FILES_BASE,
                kobj.briefy_id,
                release.split('/')[-1]
            )
        payout_value = self.parse_decimal(kobj.photographer_payout)
        knack_payout_currency = self.choice_to_str(kobj.currency_payout)
        payout_currency = str(knack_payout_currency) if knack_payout_currency else 'EUR'
        reason_compensation = self.choice_to_str(kobj.reason_for_additional_compensation)
        last_approval_date = kobj.last_approval_date
        timezone_name = kobj.timezone
        scheduled_datetime = kobj.scheduled_shoot_date_time
        if scheduled_datetime:
            scheduled_datetime = datetime_in_timezone(scheduled_datetime, timezone_name)
            scheduled_datetime = scheduled_datetime.astimezone(utc)
        payload = dict(
            id=uuid.uuid4(),
            order_id=obj.id,
            created_at=_build_date(kobj.input_date),
            updated_at=self.updated_at(kobj),
            pool=job_pool,
            reason_additional_compensation=reason_compensation or None,
            slug=self.get_slug(job_id, assignment=1),
            professional_id=professional_id,
            scheduled_datetime=scheduled_datetime,
            release_contract=release,
            payout_value=payout_value,
            payout_currency=payout_currency,
            additional_compensation=self.parse_decimal(kobj.additional_compensation) or None,
            payable=payable,
            submission_path=str(kobj.photo_submission_link),
            travel_expenses=self.parse_decimal(kobj.travel_expenses) or None,
        )
        assignment = Assignment(**payload)
        self.session.add(assignment)
        self.session.flush()
        logger.debug('Assignment added: {id}'.format(id=assignment.id))
        if professional_id:
            professional_permissions = ['view', 'edit']
            self.update_local_roles(
                assignment,
                [professional_id],
                'professional_user',
                professional_permissions
            )

        # qa manager context roles
        qa_manager_roles = self.get_local_roles(kobj, 'qa_manager')
        if last_approval_date and not qa_manager_roles:
            id_ = '0efa2980-07f9-4add-a8bf-1882a2e988e1'  # Laure
            kobj.qa_manager = [{'id': id_, 'identifier': '''Laure d'Utruy'''}]
            qa_manager_roles = [
                id_
            ]
        permissions = ['view', 'edit']
        self.update_local_roles(
            assignment,
            qa_manager_roles,
            'qa_manager',
            permissions
        )

        # scout manager context roles
        scout_manager_roles = self.get_local_roles(kobj, 'scouting_manager')
        self.update_local_roles(
            assignment,
            scout_manager_roles,
            'scout_manager',
            permissions
        )

        # project manager context roles
        pm_roles_roles = [role.user_id for role in obj.project.local_roles
                          if role.role_name.value == 'project_manager']
        self.update_local_roles(
            assignment,
            pm_roles_roles,
            'project_manager',
            permissions
        )

        # update assignment state history
        versions = self.versions.get(kobj.id, [])
        add_assignment_history(self.session, assignment, kobj, versions)
        if assignment.state == 'cancelled':
            assignment.payout_value = 0
        # add assignment comments
        self.add_assignment_comments(assignment, kobj)

        # populate the set_type field
        new_set = kobj.new_set
        further_edit = kobj.further_editing_requested_by_client

        if further_edit:
            assignment.set_type = 'refused_customer'
        elif not new_set:
            assignment.set_type = 'returned_photographer'
        else:
            assignment.set_type = 'new'
        logger.debug('Set type: {0}'.format(assignment.set_type))

    def add(self, kobj, briefy_id):
        """Add new Job to database."""
        obj = super().add(kobj, briefy_id)
        project = obj.project

        # customer context roles
        customer_roles = [role.user_id for role in project.local_roles
                          if role.role_name.value == 'customer_user']
        permissions = ['view', 'edit']
        self.update_local_roles(
            obj,
            customer_roles,
            'customer_user',
            permissions
        )

        # scout manager context roles
        scout_manager_roles = self.get_local_roles(kobj, 'scouting_manager')
        self.update_local_roles(
            obj,
            scout_manager_roles,
            'scout_manager',
            permissions
        )

        # project manager context roles
        pm_roles_roles = [role.user_id for role in project.local_roles
                          if role.role_name.value == 'project_manager']
        self.update_local_roles(
            obj,
            pm_roles_roles,
            'project_manager',
            permissions
        )

        self.add_location(obj, kobj)
        self.add_comment(obj, kobj)
        self.add_internal_comments(obj, kobj)
        self.add_assignment(obj, kobj)

        # this should be after import the assignment
        add_order_history(self.session, obj, kobj)
        logger.debug('Additional data imported for this order: History, Location, Comment.')
        return obj

    def __call__(self, knack_id=None, limit=None):
        """Syncronize one or all items from knack to sqlalchemy model."""
        self.get_version_items()
        return super().__call__(knack_id=limit)
