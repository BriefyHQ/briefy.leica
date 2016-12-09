"""Import and sync Knack Company to Leica Customer."""
from briefy.leica import logger
from briefy.leica.sync import ModelSync
from briefy.leica.models import Customer
from briefy.leica.models import CustomerContact
from briefy.leica.models import CustomerBillingAddress
from briefy.leica.sync.location import create_location_dict


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
        mobile = kobj.contact_phone.get('number') if kobj.contact_phone else ''
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

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for customer object."""
        result = super().get_payload(kobj, briefy_id)
        location_dict = create_location_dict('company_address', kobj)
        result.update(
            dict(
                external_id=kobj.id,
                title=kobj.company_name,
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
        self.add_address(kobj, obj)
        self.add_business_contact(kobj, obj)
        self.add_billing_contact(kobj, obj)
        return obj
