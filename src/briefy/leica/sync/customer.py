"""Import and sync Knack Company to Leica Customer."""
from briefy.common.db import datetime_utcnow
from briefy.common.utils.data import generate_slug
from briefy.common.utils.transformers import to_serializable
from briefy.common.users import SystemUser
from briefy.leica import logger
from briefy.leica.sync import cleanse_phone_number
from briefy.leica.sync import ModelSync
from briefy.leica.models import Customer
from briefy.leica.models import CustomerContact
from briefy.leica.models import CustomerBillingAddress
from briefy.leica.sync.location import COUNTRY_MAPPING
from briefy.leica.sync.location import create_location_dict

NOW = to_serializable(datetime_utcnow())
ACTOR = SystemUser.id


STATUS_MAPPING = {
    '@Leisure': 'active',
    'Agoda': 'active',
    'Aladinia': 'inactive',
    'Auctionata': 'inactive',
    'Beauty Spotter': 'active',
    'Booking.com': 'inactive',
    'Briefy': 'active',
    'Classic Driver': 'inactive',
    'Deliveroo Germany GmbH': 'active',
    'Deliveroo Germany': 'active',
    'DoorDash': 'inactive',
    'eH Visio': 'active',
    'Erento': 'inactive',
    'Everphone': 'inactive',
    'ezCater': 'active',
    'Foodora': 'inactive',
    'Holiday Lettings': 'inactive',
    'Homeday': 'active',
    'Hostelworld.com': 'inactive',
    'Just Eat': 'inactive',
    'Locadi': 'inactive',
    'Love Home Swap': 'inactive',
    'M Cube Incubator': 'inactive',
    'OpenTable': 'inactive',
    'OYO Rooms': 'inactive',
    'Stayz Pty': 'inactive',
    'Traveloka': 'inactive',
    'WeTravel': 'inactive',
    'Wine in Black': 'inactive',
}


class CustomerSync(ModelSync):
    """Syncronize Customers."""

    model = Customer
    knack_model_name = 'Company'

    def _add_contact(self, kobj, obj, contact_dict, knack_field):
        """Helper to add a new contact to the Customer."""
        knack_contact = getattr(kobj, knack_field)
        first_name = knack_contact.first if knack_contact.first else ''
        last_name = knack_contact.last if knack_contact.last else ''
        title = '{0} {1}'.format(first_name, last_name)

        contact_dict.update(first_name=first_name,
                            last_name=last_name,
                            title=title)
        try:
            contact = CustomerContact(**contact_dict)
            self.session.add(contact)
            self.session.flush()
        except Exception as error:
            msg = 'Failure to create {type} contact for Customer: {customer}. Error: {error}'
            logger.error(
                msg.format(
                    customer=obj.title,
                    error=error,
                    type=contact_dict.get('type')
                )
            )
        else:
            obj.contacts.append(contact)

    def add_business_contact(self, kobj, obj):
        """Add new business contact from knack instance."""
        country = COUNTRY_MAPPING.get(
            kobj.company_address.country
        )[1] if kobj.company_address.country else 'DE'
        mobile = cleanse_phone_number(
            kobj.contact_phone.get('number'),
            country
        ) if kobj.contact_phone else ''
        contact_dict = dict(
            customer_id=obj.id,
            email=kobj.email.email,
            mobile=mobile,
            type='business'
        )
        self._add_contact(kobj, obj, contact_dict, 'contact_person')

    def add_billing_contact(self, kobj, obj):
        """Create contact dict payload."""
        contact_dict = dict(
            customer_id=obj.id,
            email=kobj.billing_email.email,
            type='billing'
        )
        self._add_contact(kobj, obj, contact_dict, 'billing_contact_person')

    def _state_history(self, state: str='active'):
        """Create state history structure."""
        history = [
            {
                'date': NOW,
                'message': 'Imported customer from Knack database',
                'actor': ACTOR,
                'transition': '',
                'from': '',
                'to': 'created'
            },
            {
                'date': NOW,
                'message': 'Automatic transition',
                'actor': ACTOR,
                'transition': 'activate',
                'from': 'created',
                'to': state
            },
        ]
        if state == 'inactive':
            history.append(
                {
                    'date': NOW,
                    'message': 'Automatic transition',
                    'actor': ACTOR,
                    'transition': 'inactivate',
                    'from': 'active',
                    'to': state
                },
            )
        return history

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for customer object."""
        result = super().get_payload(kobj, briefy_id)
        location_dict = create_location_dict('company_address', kobj)
        title = kobj.company_name
        slug = generate_slug(title)
        state = STATUS_MAPPING[title]
        state_history = self._state_history(state)
        result.update(
            dict(
                external_id=kobj.id,
                slug=slug,
                state=state,
                state_history=state_history,
                title=title,
                legal_name=kobj.legal_name,
                tax_id=kobj.tax_id,
                tax_country=location_dict.get('country'),
                tax_id_type='VAT'
            )
        )
        return result

    def add_address(self, kobj, obj):
        """Add Customer address from knack object."""
        location_dict = create_location_dict('company_address', kobj)
        if not location_dict:
            return

        location_dict['customer_id'] = obj.id
        try:
            location = CustomerBillingAddress(**location_dict)
            self.session.add(location)
            self.session.flush()
        except Exception as error:
            msg = 'Failure to create location for Customer: {customer}. Error: {error}'
            logger.error(msg.format(customer=obj.title, error=error))
        else:
            obj.addresses.append(location)

    def add(self, kobj, briefy_id):
        """Add new Customer to database."""
        obj = super().add(kobj, briefy_id)

        # customer context roles
        customer_roles = self.get_local_roles(kobj, 'company_user')
        customer_permissions = ['view']
        self.update_local_roles(
            obj,
            customer_roles,
            'customer_user',
            customer_permissions
        )

        # account manager context roles
        account_roles = self.get_local_roles(kobj, 'account_manager')
        permissions = ['view', 'edit']
        self.update_local_roles(
            obj,
            account_roles,
            'account_manager',
            permissions,
        )

        self.add_address(kobj, obj)
        self.add_business_contact(kobj, obj)
        self.add_billing_contact(kobj, obj)
        return obj
