"""Import Projects to Leica."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.common.utils.data import generate_slug
from briefy.common.utils.transformers import to_serializable
from briefy.leica.config import FILES_BASE
from briefy.leica.models import Customer
from briefy.leica.models import Project
from briefy.leica.sync import category_mapping
from briefy.leica.sync import ModelSync
from briefy.leica.sync.project_constraints import CONSTRAINTS
from datetime import datetime


NOW = to_serializable(datetime_utcnow())
ACTOR = SystemUser.id


STATUS_MAPPING = {
    'Leisure Group Belvilla DE': 'ongoing',
    'Leisure Group Belvilla ES': 'ongoing',
    'Leisure Group Belvilla FR': 'ongoing',
    'Leisure Group Belvilla IT': 'ongoing',
    'Agoda Bali': 'ongoing',
    'Agoda Bangkok': 'ongoing',
    'Agoda Pattaya': 'ongoing',
    'Agoda Phuket': 'ongoing',
    'Re-shoots / New shoots': 'ongoing',
    'Aladinia Spa Project (Pilot)': 'completed',
    'Auctionata': 'completed',
    'Beauty Spotter Clinics': 'ongoing',
    'Agoda Re-shoot / New shoot': 'ongoing',
    'Classic Driver Pilot': 'completed',
    'Deliveroo Behind the Scene': 'ongoing',
    'Delivery Hero Pilot': 'ongoing',
    'Delivery Hero Cologne': 'ongoing',
    'Delivery Hero Munich': 'ongoing',
    'Delivery Hero Hamburg': 'ongoing',
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
    'Wolt Pilot': 'ongoing',
}

DATES_MAPPING = {
    'Leisure Group Belvilla DE': (
        ('2016', '05', '10', '00', '00', '00'), ('2016', '05', '10', '00', '00', '00')
    ),
    'Leisure Group Belvilla ES': (
        ('2016', '05', '10', '00', '00', '00'), ('2016', '05', '10', '00', '00', '00')
    ),
    'Leisure Group Belvilla FR': (
        ('2016', '05', '10', '00', '00', '00'), ('2016', '05', '10', '00', '00', '00')
    ),
    'Leisure Group Belvilla IT': (
        ('2016', '05', '10', '00', '00', '00'), ('2016', '05', '10', '00', '00', '00')
    ),
    'Delivery Hero Cologne': (
        ('2017', '02', '09', '00', '00', '00'), ('2017', '02', '09', '00', '00', '00')
    ),
    'Delivery Hero Hamburg': (
        ('2017', '02', '09', '00', '00', '00'), ('2017', '02', '09', '00', '00', '00')
    ),
    'Delivery Hero Munich': (
        ('2017', '02', '09', '00', '00', '00'), ('2017', '02', '09', '00', '00', '00')
    ),
    'Delivery Hero Pilot': (
        ('2017', '02', '09', '00', '00', '00'), ('2017', '02', '09', '00', '00', '00')
    ),
    'Agoda Bali': (
        ('2016', '09', '06', '00', '00', '00'), ('2016', '09', '06', '00', '00', '00')
    ),
    'Agoda Bangkok': (
        ('2016', '09', '06', '00', '00', '00'), ('2016', '09', '06', '00', '00', '00')
    ),
    'Agoda Pattaya': (
        ('2016', '12', '07', '00', '00', '00'), ('2016', '12', '07', '00', '00', '00')
    ),
    'Agoda Phuket': (
        ('2016', '12', '07', '00', '00', '00'), ('2016', '12', '07', '00', '00', '00')
    ),
    'Aladinia Spa Project (Pilot)': (
        ('2016', '08', '10', '00', '00', '00'), ('2016', '11', '21', '00', '00', '00')
    ),
    'Auctionata': (
        ('2016', '09', '15', '00', '00', '00'), ('2016', '10', '17', '00', '00', '00')
    ),
    'Beauty Spotter Clinics': (
        ('2016', '06', '21', '00', '00', '00'), ('2016', '06', '21', '00', '00', '00')
    ),
    'Re-shoots / New shoots': (
        ('2016', '06', '01', '00', '00', '00'), ('2016', '06', '01', '00', '00', '00')
    ),
    'Classic Driver Pilot': (
        ('2016', '08', '30', '00', '00', '00'), ('2016', '09', '07', '00', '00', '00')
    ),
    'Deliveroo Behind the Scene': (
        ('2016', '11', '14', '00', '00', '00'), ('2016', '11', '14', '00', '00', '00')
    ),
    'eH Visio Clinics': (
        ('2016', '06', '21', '00', '00', '00'), ('2016', '06', '21', '00', '00', '00')
    ),
    'Erento': (
        ('2016', '01', '26', '00', '00', '00'), ('2016', '06', '22', '00', '00', '00')
    ),
    'Everphone Business Portrait': (
        ('2016', '07', '21', '00', '00', '00'), ('2016', '08', '02', '00', '00', '00')
    ),
    'ezCater USA': (
        ('2016', '06', '30', '00', '00', '00'), ('2016', '06', '30', '00', '00', '00')
    ),
    'Foodora Wien': (
        ('2016', '04', '12', '00', '00', '00'), ('2016', '06', '30', '00', '00', '00')
    ),
    'Homeday Properties': (
        ('2016', '06', '21', '00', '00', '00'), ('2016', '06', '21', '00', '00', '00')
    ),
    'Homeday Portraits': (
        ('2016', '06', '21', '00', '00', '00'), ('2016', '06', '21', '00', '00', '00')
    ),
    'Just Eat finalists UK': (
        ('2016', '10', '24', '00', '00', '00'), ('2016', '11', '22', '00', '00', '00')
    ),
    'Love Home Swap': (
        ('2015', '10', '15', '00', '00', '00'), ('2016', '08', '17', '00', '00', '00')
    ),
    'Stayz Australia': (
        ('2016', '05', '15', '00', '00', '00'), ('2016', '07', '29', '00', '00', '00')
    ),
    'WeTravel Yoga': (
        ('2016', '08', '10', '00', '00', '00'), ('2016', '09', '30', '00', '00', '00')
    ),
    'Wolt Pilot': (
        ('2017', '01', '01', '00', '00', '00'), ('2017', '01', '01', '00', '00', '00')
    ),
}


class ProjectSync(ModelSync):
    """Syncronize Projects."""

    model = Project
    knack_model_name = 'Project'
    knack_parent_model = 'Company'
    parent_model = Customer

    def _state_history(self, state: str, created_at: datetime, updated_at: datetime):
        """Create state history structure."""
        created_at = to_serializable(created_at)
        updated_at = to_serializable(updated_at)
        history = [
            {
                'date': created_at,
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
                        'date': created_at,
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
                        'date': updated_at,
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
                        'date': updated_at,
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
        raw_dates = DATES_MAPPING[title]
        created_at = datetime(*[int(p) for p in raw_dates[0]])
        updated_at = datetime(*[int(p) for p in raw_dates[0]])
        state = STATUS_MAPPING[title]
        state_history = self._state_history(state, created_at, updated_at)
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
                category=category_mapping.get(category, 'undefined'),
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
                created_at=created_at,
                updated_at=updated_at,
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
