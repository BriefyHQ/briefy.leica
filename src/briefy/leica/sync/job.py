"""Import and sync Knack Job to Leica Job."""
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica import logger
from briefy.leica.config import FILES_BASE
from briefy.leica.models import Comment
from briefy.leica.models import Assignment
from briefy.leica.models import OrderLocation
from briefy.leica.models import Order
from briefy.leica.models import Pool
from briefy.leica.models import Project
from briefy.leica.vocabularies import OrderInputSource as ISource
from briefy.leica.sync import PLACEHOLDERS
from briefy.leica.sync import ModelSync
from briefy.leica.sync.job_wf_history import _build_date
from briefy.leica.sync.job_wf_history import add_assignment_history
from briefy.leica.sync.job_wf_history import add_order_history
from briefy.leica.sync.location import create_location_dict

import uuid

isource_mapping = {item.label: item.value for item in ISource.__members__.values()}
category_mapping = {item.label: item.value for item in CategoryChoices.__members__.values()}


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
        number_required_assets = kobj.number_of_photos or project.number_required_assets or 10
        category = kobj.category.pop() if kobj.category else 'undefined'
        category = 'Accommodation' if category == 'Accomodation' else category
        category = 'Portrait' if category == 'Portraits' else category
        if kobj.availability_1 and kobj.availability_2:
            availability = [
                kobj.availability_1.isoformat(),
                kobj.availability_2.isoformat()
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

        order_payload.update(
            dict(
                title=kobj.job_name,
                description='',
                created_at=_build_date(kobj.input_date),
                category=category_mapping.get(category, 'undefined'),
                project_id=project.id,
                customer_id=project.customer.id,
                price=self.parse_decimal(kobj.set_price),
                customer_order_id=kobj.job_id,
                slug=self.get_slug(job_id),
                delivery=delivery,
                job_id=job_id,
                availability=availability,
                external_id=kobj.id,
                requirements=requirements,
                number_required_assets=number_required_assets,
                source=isource_mapping.get(str(kobj.input_source), 'briefy'),
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

    def add_comment(self, obj, kobj):
        """Add Project Manager comment to the Order."""
        if kobj.project_manager_comment:
            project_manager = obj.project.project_manager if obj.project.project_manager else None
            payload = dict(
                id=uuid.uuid4(),
                entity_id=obj.id,
                entity_type=obj.__tablename__,
                author_id=project_manager,
                content=kobj.project_manager_comment,
                author_role='project_manager',
                to_role='customer_user',
                internal=False,
            )
            session = self.session
            session.add(Comment(**payload))

        if kobj.client_feedback:
            customer_user = obj.project.customer_user or obj.project.project_manager
            payload = dict(
                id=uuid.uuid4(),
                entity_id=obj.id,
                entity_type=obj.__tablename__,
                author_id=customer_user,
                content=kobj.client_feedback,
                author_role='customer_user',
                to_role='project_manager',
                internal=False,
            )
            session = self.session
            session.add(Comment(**payload))

    def add_assignment_comments(self, obj, kobj):
        """Import Assignment comments."""
        if kobj.photographers_comment and obj.professional_id:
            payload = dict(
                id=uuid.uuid4(),
                entity_id=obj.id,
                entity_type=obj.__tablename__,
                author_id=obj.professional_id,
                content=kobj.photographers_comment,
                author_role='professional_user',
                to_role='qa_manager',
                internal=False,
            )
            session = self.session
            session.add(Comment(**payload))

        if kobj.quality_assurance_feedback:
            qa_manager = obj.qa_manager or obj.project.project_manager
            payload = dict(
                id=uuid.uuid4(),
                entity_id=obj.id,
                entity_type=obj.__tablename__,
                author_id=qa_manager,
                content=kobj.quality_assurance_feedback,
                author_role='qa_manager',
                to_role='professional_user',
                internal=False,
            )
            session = self.session
            session.add(Comment(**payload))

    def add_assignment(self, obj, kobj):
        """Add a related assign object."""
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
        payload = dict(
            id=uuid.uuid4(),
            order_id=obj.id,
            created_at=_build_date(kobj.input_date),
            pool=job_pool,
            reason_additional_compensation=reason_compensation,
            slug=self.get_slug(job_id, assignment=1),
            professional_id=professional_id,
            scheduled_datetime=kobj.scheduled_shoot_date_time,
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
        add_assignment_history(self.session, assignment, kobj)
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
        self.add_assignment(obj, kobj)

        # this should be after import the assignment
        add_order_history(self.session, obj, kobj)
        logger.debug('Additional data imported for this order: History, Location, Comment.')
        return obj
