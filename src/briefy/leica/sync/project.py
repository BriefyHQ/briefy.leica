"""Import Projects to Leica."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.common.utils.data import generate_slug
from briefy.common.utils.transformers import to_serializable
from briefy.leica.models import Customer
from briefy.leica.models import Project
from briefy.leica.sync import ModelSync
from briefy.leica.sync.project_constraints import CONSTRAINTS

NOW = to_serializable(datetime_utcnow())
ACTOR = SystemUser.id


class ProjectSync(ModelSync):
    """Syncronize Projects."""

    model = Project
    knack_model_name = 'Project'
    knack_parent_model = 'Company'
    parent_model = Customer

    def _state_history(self, state: str='ongoing'):
        """Create state history structure."""
        return [
            {
                'date': NOW,
                'message': 'Imported project from Knack database',
                'actor': ACTOR,
                'transition': '',
                'from': '',
                'to': 'created'
            },
            {
                'date': NOW,
                'message': 'Automatic transition',
                'actor': ACTOR,
                'transition': 'start' if state == 'ongoing' else 'pause',
                'from': 'created',
                'to': state
            },
        ]

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for project object."""
        result = super().get_payload(kobj, briefy_id)
        customer, company = self.get_parent(kobj, 'company')

        # TODO: 'project_comment' but not really used on knack

        title = kobj.project_name.strip()
        slug = generate_slug(title)
        tech_requirements = CONSTRAINTS[title]
        state = 'ongoing'
        state_history = self._state_history(state)
        result.update(
            dict(
                title=title,
                slug=slug,
                state=state,
                state_history=state_history,
                description='',
                abstract=kobj.project_abstract,
                customer_id=customer.id,
                briefing=kobj.briefing,
                approval_window=kobj.set_refusal_window or 0,
                number_required_assets=kobj.number_required_assets,
                availability_window=kobj.availability_window or 0,
                payout_currency=kobj.currency_set_price or 'EUR',
                payout_value=self.parse_decimal(kobj.project_payout_set_price),
                cancellation_window=kobj.cancellation_window or 0,
                contract=company.link_to_contract.url,
                price=self.parse_decimal(kobj.project_set_price),
                price_currency=kobj.currency_set_price or 'EUR',
                external_id=kobj.id,
                release_template=kobj.release_template,
                tech_requirements=tech_requirements
            )
        )
        return result

    def add(self, kobj, briefy_id):
        """Add new Project to database."""
        obj = super().add(kobj, briefy_id)

        # briefy project manager context roles
        pm_briefy_roles = self.get_local_roles(kobj, 'project_manager')
        permissions = ['view', 'edit']
        self.update_local_roles(
            obj,
            pm_briefy_roles,
            'project_manager',
            permissions
        )

        # customer pm user context roles
        customer_roles = self.get_local_roles(kobj, 'clients_project_manager')
        customer_permissions = ['view']
        self.update_local_roles(
            obj,
            customer_roles,
            'customer_user',
            customer_permissions
        )

        return obj
