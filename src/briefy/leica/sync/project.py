"""Import Projects to Leica."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.common.utils.data import generate_slug
from briefy.common.utils.transformers import to_serializable
from briefy.leica.config import FILES_BASE
from briefy.leica.models import Customer
from briefy.leica.models import Project
from briefy.leica.sync import ModelSync
from briefy.leica.sync import category_mapping
from briefy.leica.sync.project_constraints import CONSTRAINTS

NOW = to_serializable(datetime_utcnow())
ACTOR = SystemUser.id


STATUS_MAPPING = {
    'Leisure Group Belvilla DE': 'paused',
    'Leisure Group Belvilla ES': 'paused',
    'Leisure Group Belvilla FR': 'paused',
    'Leisure Group Belvilla IT': 'paused',
    'Agoda Bali': 'ongoing',
    'Agoda Bangkok': 'ongoing',
    'Agoda Pattaya': 'ongoing',
    'Agoda Phuket': 'ongoing',
    'Aladinia Spa Project (Pilot)': 'completed',
    'Auctionata': 'completed',
    'Beauty Spotter Clinics': 'ongoing',
    'Agoda Re-shoot / New shoot': 'ongoing',
    'Classic Driver Pilot': 'completed',
    'Deliveroo Behind the Scene': 'ongoing',
    'eH Visio Clinics': 'ongoing',
    'Erento': 'completed',
    'Everphone Business Portrait': 'completed',
    'ezCater USA': 'ongoing',
    'Foodora Wien': 'completed',
    'Homeday Properties': 'created',
    'Homeday Portraits': 'ongoing',
    'Just Eat finalists UK': 'completed',
    'Love Home Swap': 'completed',
    'Stayz Australia': 'completed',
    'WeTravel Yoga': 'completed',
}


class ProjectSync(ModelSync):
    """Syncronize Projects."""

    model = Project
    knack_model_name = 'Project'
    knack_parent_model = 'Company'
    parent_model = Customer

    def _state_history(self, state: str='ongoing'):
        """Create state history structure."""
        history = [
            {
                'date': NOW,
                'message': 'Imported project from Knack database',
                'actor': ACTOR,
                'transition': '',
                'from': '',
                'to': 'created'
            },
        ]
        if state in ('ongoing', 'paused', 'completed'):
            history.append(
                    {
                        'date': NOW,
                        'message': 'Automatic transition',
                        'actor': ACTOR,
                        'transition': 'start',
                        'from': 'created',
                        'to': 'ongoing',
                    },
            )
            if state == 'paused':
                history.append(
                    {
                        'date': NOW,
                        'message': 'Automatic transition',
                        'actor': ACTOR,
                        'transition': 'pause',
                        'from': 'ongoing',
                        'to': 'paused',
                    },
                )
            if state == 'completed':
                history.append(
                    {
                        'date': NOW,
                        'message': 'Automatic transition',
                        'actor': ACTOR,
                        'transition': 'close',
                        'from': 'ongoing',
                        'to': 'completed',
                    },
                )
        return history

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for project object."""
        result = super().get_payload(kobj, briefy_id)
        customer, company = self.get_parent(kobj, 'company')

        # TODO: 'project_comment' but not really used on knack

        title = kobj.project_name.strip()
        slug = generate_slug(title)
        tech_requirements = CONSTRAINTS[title]
        state = STATUS_MAPPING[title]
        state_history = self._state_history(state)
        briefing = kobj.briefing
        if briefing:
            briefing = '{0}/files/projects/{1}/briefing/{2}'.format(
                FILES_BASE,
                kobj.briefy_id,
                briefing.split('/')[-1]
            )
        release_template = kobj.release_template
        if release_template:
            release_template = '{0}/files/projects/{1}/release_template/{2}'.format(
                FILES_BASE,
                kobj.briefy_id,
                release_template.split('/')[-1]
            )

        category = kobj.category.pop() if kobj.category else 'undefined'
        category = 'Accommodation' if category == 'Accomodation' else category
        category = 'Portrait' if category == 'Portraits' else category

        knack_price_currency = self.choice_to_str(kobj.currency_set_price)
        price_currency = str(knack_price_currency) if knack_price_currency else 'EUR'
        result.update(
            dict(
                title=title,
                slug=slug,
                state=state,
                category=category,
                state_history=state_history,
                description='',
                abstract=kobj.project_abstract,
                customer_id=customer.id,
                briefing=briefing,
                approval_window=kobj.set_refusal_window or 0,
                number_required_assets=kobj.number_required_assets,
                availability_window=kobj.availability_window or 0,
                payout_currency=price_currency,
                payout_value=self.parse_decimal(kobj.project_payout_set_price),
                cancellation_window=kobj.cancellation_window or 0,
                contract=company.link_to_contract.url,
                price=self.parse_decimal(kobj.project_set_price),
                price_currency=price_currency,
                external_id=kobj.id,
                release_template=release_template,
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
