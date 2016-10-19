from briefy.leica.models import Customer
from briefy.leica.models import Project
from briefy.leica.sync import ModelSync


class ProjectSync(ModelSync):
    """Syncronize Projects."""

    model = Project
    knack_model_name = 'Project'

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for customer object."""
        result = super().get_payload(kobj, briefy_id)
        customer = Customer.query().filter_by(external_id=kobj.company[0]['id']).one()
        result.update(
            dict(
                customer=customer,
                external_id=kobj.id,
                title=kobj.project_name.strip() or 'Undefined',
                project_manager=self.get_user(kobj, 'project_manager'),
                tech_requirements={'dimension': '4000x3000'}
            )
        )
        return result
