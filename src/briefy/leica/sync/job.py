"""Import and sync Knack Job to Leica Job."""
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica import logger
from briefy.leica.models import Comment
from briefy.leica.models import JobAssignment
from briefy.leica.models import JobLocation
from briefy.leica.models import JobOrder
from briefy.leica.models import Project
from briefy.leica.sync import ModelSync
from briefy.leica.sync.location import create_location_dict
from briefy.leica.vocabularies import JobInputSource as ISource


job_status_mapping = {
    'Pending': 'pending',
    'Published': 'published',
    'Scheduled': 'scheduled',
    'Assigned': 'assigned',
    'Cancelled ': 'cancelled',
    'Awaiting Assets': 'awaiting_assets',
    'Approved': 'approved',
    'Completed': 'completed',
    'Refused': 'refused',
    'In QA': 'in_qa',
}

isource_mapping = {item.label: item.value for item in ISource.__members__.values()}
category_mapping = {item.label: item.value for item in CategoryChoices.__members__.values()}


class JobSync(ModelSync):
    """Syncronize Jobs."""

    model = JobOrder
    knack_model_name = 'Job'
    knack_parent_model = 'Project'
    parent_model = Project
    bulk_insert = False

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for customer object."""

        order_payload = super().get_payload(kobj, briefy_id)
        project, kproject = self.get_parent(kobj, 'project')

        order_payload.update(
            dict(
                title=kobj.job_name,
                description='',
                category=category_mapping.get(str(kobj.category), 'undefined'),
                project_id=project.id,
                customer_id=project.customer.id,
                price=self.parse_decimal(kobj.set_price),
                customer_order_id=kobj.job_id,
                job_id=kobj.internal_job_id or kobj.job_id,
                external_id=kobj.id,
                requirements=kobj.client_specific_requirement,
                number_of_assets=kobj.number_of_photos,
                source=isource_mapping.get(str(kobj.input_source), 'briefy'),
            )
        )
        return order_payload

    def add_history(self, obj, kobj):
        """Add state_history and state information to the Order."""
        knack_status = list(kobj.approval_status)
        if knack_status:
            state = job_status_mapping.get(knack_status[0])
        else:
            msg = 'Status was not found in the mapping. Job ID {job_id}'
            logger.info(msg.format(job_id=obj.customer_order_id))
            state = 'pending'
        history = dict(
            message='Imported in this state from Knack database',
            actor='g:system',
            transition='',
            to=state
        )
        obj.state_history = [history]
        obj.state = state
        self.session.add(obj)
        model = obj.__class__.__name__
        logger.debug('{model} imported with state: {state}'.format(model=model, state=state))

    def add_location(self, obj, kobj):
        """Add Job location to the Order."""
        payload = create_location_dict('job_location', kobj)
        if payload:
            payload['order_id'] = obj.id
            payload.update(
                mobile=self.parse_phonenumber(kobj, 'contact_number_1'),
                additional_phone=self.parse_phonenumber(kobj, 'contact_number_2'),
                email=kobj.contact_email.email or 'abc123@gmail.com',
                first_name=kobj.contact_person.first or 'first name',
                last_name=kobj.contact_person.last or 'last name',
            )
            try:
                location = JobLocation(**payload)
                self.session.add(location)
                obj.locations.append(location)
                self.session.flush()
            except Exception as exc:
                print(exc)
        else:
            msg = 'Failure to create location for Job: {job}, no location found.'
            logger.info(msg.format(job=obj.customer_order_id))

    def add_comment(self, obj, kobj):
        """Add Project Manager comment to the Order."""
        project_manager = obj.project.project_manager[0] if obj.project.project_manager else None
        payload = dict(
            entity_id=obj.id,
            entity_type=obj.__tablename__,
            author_id=project_manager,
            content=kobj.project_manager_comment
        )
        session = self.session
        session.add(Comment(**payload))
        session.flush()

    def add_assigment_comments(self, obj, kobj):
        """Import assigment comments"""
        # TODO: internal comment, photographer comment, quality assurance feedback
        pass

    def add_assigment(self, obj, kobj):
        """Add a related assign object."""
        # TODO: dates should be created as workflow history transitions
        # assignment_date = kobj.assignment_date
        # add comments

        payable = True
        if kobj.approval_status == {'Cancelled'}:
            payable = False

        professional_id = self.get_user(kobj, 'responsible_photographer')
        payload = dict(
            order_id=obj.id,
            professional_id=professional_id,
            payout_value=self.parse_decimal(kobj.photographer_payout),
            payout_currency=kobj.currency_payout or 'EUR',
            additional_compensation=self.parse_decimal(kobj.additional_compensation),
            payable=payable,
            submission_path=str(kobj.photo_submission_link),
            travel_expenses=self.parse_decimal(kobj.travel_expenses),
        )
        assignment = JobAssignment(**payload)
        self.session.add(assignment)
        self.session.flush()
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
        pm_roles_roles = [user_id for user_id in obj.project.project_manager]
        self.update_local_roles(assignment, pm_roles_roles, 'project_manager')

        # update assignment state history
        self.add_history(assignment, kobj)

    def add(self, kobj, briefy_id):
        """Add new Job to database."""
        obj = super().add(kobj, briefy_id)

        # customer context roles
        customer_roles = [user_id for user_id in obj.project.customer_user]
        self.update_local_roles(obj, customer_roles, 'customer_user')

        # scout manager context roles
        scout_manager_roles = self.get_local_roles(kobj, 'scouting_manager')
        self.update_local_roles(obj, scout_manager_roles, 'scout_manager')

        # project manager context roles
        pm_roles_roles = [user_id for user_id in obj.project.project_manager]
        self.update_local_roles(obj, pm_roles_roles, 'project_manager')

        self.add_history(obj, kobj)
        self.add_location(obj, kobj)
        self.add_comment(obj, kobj)
        self.add_assigment(obj, kobj)
        logger.info('Additional data imported for this order: History, Location, Comment.')
        return obj
