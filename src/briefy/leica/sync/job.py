from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica.models import Job
from briefy.leica.models import Project
from briefy.leica.sync import ModelSync
from briefy.leica.sync.job_location import create_location


# Initial workflow state based on field ['client_job_status']
knack_status_mapping = {
  'Job received': 'pending',
  'In scheduling process': 'scheduling',
  'Scheduled': 'scheduled',
  'In QA process': 'in_qa',
  'Completed': 'approved',
  'In revision ': 'revision',
  'Resolved': 'completed',
  'Cancelled ': 'cancelled'
}


class JobSync(ModelSync):
    """Syncronize Jobs."""

    model = Job
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
                job_requirements=kobj.client_specific_requirement,
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

        knack_status = list(kobj.client_job_status)
        if knack_status:
            status = knack_status_mapping.get(knack_status[0], 'in_qa')
        else:
            status = 'in_qa'

        history = dict(
            message='Imported in this state from Knack database',
            actor='g:system',
            to=status
        )
        obj.state_history = [history]
        obj.status = status

        location_dict = kobj.__dict__['job_location']
        job_location = create_location(location_dict, obj, self.session)
        if job_location:
            obj.job_locations.append(job_location)

        return obj
