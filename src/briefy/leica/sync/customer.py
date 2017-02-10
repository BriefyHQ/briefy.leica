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
from datetime import datetime

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
    'Delivery Hero': 'active',
    'DoorDash': 'inactive',
    'eH Visio': 'active',
    'Erento': 'inactive',
    'Everphone': 'inactive',
    'ezCater': 'active',
    'Foodora': 'inactive',
    'Holiday Lettings': 'inactive',
    'Homeday': 'active',
    'Hostelworld.com': 'inactive',
    'Just Eat': 'active',
    'Locadi': 'inactive',
    'Love Home Swap': 'inactive',
    'M Cube Incubator': 'inactive',
    'OpenTable': 'inactive',
    'OYO Rooms': 'inactive',
    'Stayz Pty': 'inactive',
    'Traveloka': 'inactive',
    'WeTravel': 'inactive',
    'Wine in Black': 'inactive',
    'Wolt': 'active',
}

DATES_MAPPING = {
    '@Leisure': (
        ('2016', '05', '10', '00', '00', '00'), ('2016', '05', '10', '00', '00', '00')
    ),
    'Delivery Hero': (
        ('2017', '02', '09', '00', '00', '00'), ('2017', '02', '09', '00', '00', '00')
    ),
    'Agoda': (
        ('2016', '09', '06', '00', '00', '00'), ('2016', '09', '06', '00', '00', '00')
    ),
    'Aladinia': (
        ('2015', '11', '03', '00', '00', '00'), ('2016', '11', '21', '00', '00', '00')
    ),
    'Auctionata': (
        ('2016', '09', '15', '00', '00', '00'), ('2016', '10', '17', '00', '00', '00')
    ),
    'Beauty Spotter': (
        ('2016', '06', '21', '00', '00', '00'), ('2016', '06', '21', '00', '00', '00')
    ),
    'Briefy': (
        ('2013', '02', '01', '00', '00', '00'), ('2016', '06', '01', '00', '00', '00')
    ),
    'Classic Driver': (
        ('2016', '08', '30', '00', '00', '00'), ('2016', '09', '07', '00', '00', '00')
    ),
    'Deliveroo Germany GmbH': (
        ('2016', '11', '14', '00', '00', '00'), ('2016', '11', '14', '00', '00', '00')
    ),
    'Deliveroo Germany': (
        ('2016', '11', '14', '00', '00', '00'), ('2016', '11', '14', '00', '00', '00')
    ),
    'eH Visio': (
        ('2016', '06', '21', '00', '00', '00'), ('2016', '06', '21', '00', '00', '00')
    ),
    'Erento': (
        ('2016', '01', '26', '00', '00', '00'), ('2016', '06', '22', '00', '00', '00')
    ),
    'Everphone': (
        ('2016', '07', '21', '00', '00', '00'), ('2016', '08', '02', '00', '00', '00')
    ),
    'ezCater': (
        ('2016', '06', '30', '00', '00', '00'), ('2016', '06', '30', '00', '00', '00')
    ),
    'Foodora': (
        ('2016', '04', '12', '00', '00', '00'), ('2016', '06', '30', '00', '00', '00')
    ),
    'Holiday Lettings': (
        ('2015', '09', '21', '00', '00', '00'), ('2016', '06', '21', '00', '00', '00')
    ),
    'Homeday': (
        ('2016', '06', '21', '00', '00', '00'), ('2016', '06', '21', '00', '00', '00')
    ),
    'Hostelworld.com': (
        ('2015', '06', '01', '00', '00', '00'), ('2015', '06', '01', '00', '00', '00')
    ),
    'Just Eat': (
        ('2016', '02', '01', '00', '00', '00'), ('2016', '02', '01', '00', '00', '00')
    ),
    'Locadi': (
        ('2015', '08', '01', '00', '00', '00'), ('2016', '08', '17', '00', '00', '00')
    ),
    'Love Home Swap': (
        ('2015', '10', '15', '00', '00', '00'), ('2016', '08', '17', '00', '00', '00')
    ),
    'Stayz Pty': (
        ('2016', '05', '15', '00', '00', '00'), ('2016', '07', '29', '00', '00', '00')
    ),
    'WeTravel': (
        ('2016', '08', '10', '00', '00', '00'), ('2016', '09', '30', '00', '00', '00')
    ),
    'Wine in Black': (
        ('2015', '12', '22', '00', '00', '00'), ('2017', '01', '01', '00', '00', '00')
    ),
    'Wolt': (
        ('2017', '01', '01', '00', '00', '00'), ('2017', '01', '01', '00', '00', '00')
    ),
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
            country,
            kobj
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

    def _state_history(self, state: str, created_at: datetime, updated_at: datetime):
        """Create state history structure."""
        created_at = to_serializable(created_at)
        updated_at = to_serializable(updated_at)
        history = [
            {
                'date': created_at,
                'message': 'Imported customer from Knack database',
                'actor': ACTOR,
                'transition': '',
                'from': '',
                'to': 'created'
            },
            {
                'date': created_at,
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
                    'date': updated_at,
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
        raw_dates = DATES_MAPPING[title]
        created_at = datetime(*[int(p) for p in raw_dates[0]])
        updated_at = datetime(*[int(p) for p in raw_dates[0]])
        state = STATUS_MAPPING[title]
        state_history = self._state_history(state, created_at, updated_at)
        result.update(
            dict(
                created_at=created_at,
                updated_at=updated_at,
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
