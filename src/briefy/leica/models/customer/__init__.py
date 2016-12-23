"""Briefy Leica Customer model."""
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.customer import workflows
from briefy.ws.utils.user import add_user_info_to_state_history
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from zope.interface import Interface
from zope.interface import implementer

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class ICustomer(Interface):
    """Marker interface for a Customer"""


class TaxInfo:
    """Tax information"""

    tax_id = sa.Column(
        sa.String(50), nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Tax ID',
                'missing': None,
                'typ': colander.String
            }
        }
    )
    """Tax ID for this customer.

    i.e.: 256.018.208-49
    """

    tax_id_type = sa.Column(
        sa.String(50), nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Tax ID type',
                'missing': None,
                'typ': colander.String
            }
        }
    )
    """Tax ID type.

    i.e.: CPF
    """

    tax_country = sa.Column(
        sautils.CountryType, nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Tax Country',
                'missing': None,
                'typ': colander.String
            }
        }
    )
    """Tax Country

    i.e.: BR
    """


@implementer(ICustomer)
class Customer(TaxInfo, mixins.PolaroidMixin, mixins.CustomerBriefyRoles,
               mixins.KLeicaVersionedMixin, Base):
    """A Customer for Briefy."""

    _workflow = workflows.CustomerWorkflow

    __summary_attributes__ = [
        'id', 'slug', 'title', 'description', 'created_at', 'updated_at', 'state', 'external_id'
    ]

    __listing_attributes__ = __summary_attributes__

    __colanderalchemy_config__ = {'excludes': [
        'state_history', 'state', '_account_manager', '_customer_user',
        'billing_contact', 'business_contact'
    ]}

    parent_customer_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('customers.id'),
        nullable=True,
        info={'colanderalchemy': {
                'title': 'Customer',
                'missing': None,
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
     )
    """Parent Customer ID.

    Auto reference to represent composed companies :class:`briefy.leica.models.customer.Customer`.
    """

    legal_name = sa.Column(
        sa.String(255),
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Customer Legal name',
                'missing': None,
                'typ': colander.String
            }
        }
    )
    """Legal name of the company.

    i.e.: Insta Stock GmbH
    """

    addresses = orm.relationship(
        'CustomerBillingAddress',
        backref=orm.backref('customer', lazy='joined'),
        lazy='dynamic',
    )
    """List of Billing Addresses for a Customer

    Returns a collection of :class:`briefy.leica.models.customer.address.CustomerBillingAddress`.
    """

    contacts = orm.relationship(
        'CustomerContact',
        backref=orm.backref('customer'),
        lazy='dynamic'
    )
    """List of Contacts for a Customer

    Returns a collection of :class:`briefy.leica.models.customer.contact.CustomerContact`.
    """

    business_contact = orm.relationship(
        'CustomerContact',
        primaryjoin='''and_(
            Customer.id == CustomerContact.customer_id,
            CustomerContact.type == "business"
        )''',
        viewonly=True,
        uselist=False,
    )
    """Customer business contact.

    Returns an instance of :class:`briefy.leica.models.customer.contact.CustomerContact`.
    """

    billing_contact = orm.relationship(
        'CustomerContact',
        primaryjoin='''and_(
            Customer.id == CustomerContact.customer_id,
            CustomerContact.type == "billing"
        )''',
        viewonly=True,
        uselist=False,
    )
    """Customer billing contact.

    Returns an instance of :class:`briefy.leica.models.customer.contact.CustomerContact`.
    """

    projects = orm.relationship(
        'Project',
        backref=orm.backref('customer'),
        lazy='dynamic'
    )
    """List of Projects of this Customer.

    Returns a collection of :class:`briefy.leica.models.project.Project`.
    """

    jobs = orm.relationship(
        'JobOrder',
        backref=orm.backref('customer'),
        lazy='dynamic'
    )
    """List of Jobs of this Customer.

    Returns a collection of :class:`briefy.leica.models.job.order.JobOrders`.
    """

    @declared_attr
    def _external_model_(cls):
        """Name of the model on Knack."""
        return 'Company'

    def to_listing_dict(self) -> dict:
        """Return a summarized version of the dict representation of this Class.

        Used to serialize this object within a parent object serialization.
        :returns: Dictionary with fields and values used by this Class
        """
        billing_contact = self.billing_contact
        business_contact = self.business_contact
        data = super().to_listing_dict()
        data = self._apply_actors_info(data)
        data['billing_contact'] = billing_contact.to_summary_dict() if billing_contact else None
        data['business_contact'] = business_contact.to_summary_dict() if business_contact else None
        return data

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['slug'] = self.slug
        addresses = [address.to_dict(excludes='customer') for address in self.addresses.all()]
        data.update(addresses=addresses)
        add_user_info_to_state_history(self.state_history)
        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data
