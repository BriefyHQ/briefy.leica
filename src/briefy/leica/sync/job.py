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
        get_user = self.get_user
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
                qa_manager=get_user(kobj, 'qa_manager'),
                scout_manager=get_user(kobj, 'scouting_manager'),
                project_manager=get_user(kobj, 'project_manager')
            )
        )
        return order_payload

    def add_history(self, obj, kobj):
        """Add state_history and state information to the Order."""
        knack_status = list(kobj.approval_status)
        if knack_status:
            status = job_status_mapping.get(knack_status[0])
        else:
            msg = 'Status was not found in the mapping. Job ID {job_id}'
            logger.info(msg.format(job_id=obj.customer_order_id))
            status = 'pending'
        history = dict(
            message='Imported in this state from Knack database',
            actor='g:system',
            to=status
        )
        obj.state_history = [history]
        obj.status = status

    def add_location(self, obj, kobj):
        """Add Job location to the Order."""
        payload = create_location_dict('job_location', kobj)
        if payload:
            payload['order_id'] = obj.id
            additional_phone = kobj.contact_number_2
            additional_phone = additional_phone.get('number') if additional_phone else None
            payload.update(
                mobile=kobj.contact_number_1.get('number') if kobj.contact_number_1 else None,
                additional_phone=additional_phone,
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
        payload = dict(
            entity_id=obj.id,
            entity_type=obj.__tablename__,
            author_id=obj.project.project_manager[0].id if obj.project.project_manager else None,
            content=kobj.project_manager_comment
        )
        session = self.session
        session.add(Comment(**payload))
        session.flush()

    def add_assigment(self, obj, kobj):
        """Add a related assign object."""
        # TODO: dates should be created as workflow history transitions
        # assignment_date = kobj.assignment_date

        payload = dict(
            professional_id=self.get_user(kobj, 'responsible_photographer'),
        )
        return JobAssignment(**payload)

    def add(self, kobj, briefy_id):
        """Add new Job to database."""
        obj = super().add(kobj, briefy_id)
        try:
            self.add_history(obj, kobj)
            self.add_location(obj, kobj)
            self.add_comment(obj, kobj)
        except Exception as exc:
            print(exc)
        else:
            logger.info('Additional data imported for this order: History, Location, Comment.')
        return obj
