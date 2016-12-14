"""Import and sync Knack Job to Leica Job."""
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica import logger
from briefy.leica.models import JobAssignment
from briefy.leica.models import JobLocation
from briefy.leica.models import Project
from briefy.leica.sync import ModelSync
from briefy.leica.sync.location import create_location_dict


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


class JobSync(ModelSync):
    """Syncronize Jobs."""

    model = JobAssignment
    knack_model_name = 'Job'

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for customer object."""
        result = super().get_payload(kobj, briefy_id)
        get_user = self.get_user

        # TODO: create a smart enum that can retrieve enum members by value:
        category = CategoryChoices.accommodation
        project = Project.query().filter_by(external_id=kobj.project[0]['id']).one()

        result.update(
            dict(
                title=kobj.job_name or kobj.id,
                category=category,
                project=project,
                customer_job_id=kobj.job_id,
                job_id=kobj.internal_job_id or kobj.job_name or kobj.id,
                external_id=kobj.id,
                requirements=kobj.client_specific_requirement,
                number_of_assets=kobj.number_of_photos,
                assignment_date=kobj.assignment_date,
                professional_id=get_user(kobj, 'responsible_photographer'),
                qa_manager=get_user(kobj, 'qa_manager'),
                scout_manager=get_user(kobj, 'scouting_manager'),
            )
        )
        return result

    def add(self, kobj, briefy_id):
        """Add new Job to database."""
        obj = super().add(kobj, briefy_id)

        knack_status = list(kobj.approval_status)
        if knack_status:
            status = job_status_mapping.get(knack_status[0])
        else:
            status = 'pending'

        history = dict(
            message='Imported in this state from Knack database',
            actor='g:system',
            to=status
        )
        obj.state_history = [history]
        obj.status = status

        location_dict = create_location_dict('job_location', kobj)
        if location_dict:
            location_dict['job_id'] = obj.id

        try:
            location = JobLocation(**location_dict)
            self.session.add(location)
            self.session.flush()
        except Exception as error:
            msg = 'Failure to create location for Job: {job}. Error: {error}'
            logger.error(msg.format(job=obj.customer_job_id, error=error))
        else:
            obj.job_locations.append(location)

        return obj
