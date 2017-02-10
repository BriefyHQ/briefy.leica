"""Briefy Leica Customer model."""
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.customer import workflows
from briefy.leica.utils.user import add_user_info_to_state_history
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from zope.interface import Interface
from zope.interface import implementer

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class ICustomer(Interface):
    """Marker interface for a Customer."""


class TaxInfo:
    """Tax information."""

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
                'missing': colander.drop,
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
                'missing': colander.drop,
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
        'id', 'slug', 'title', 'description', 'created_at', 'updated_at', 'state',
        'tax_country', 'legal_name'
    ]
    __summary_attributes_relations__ = [
        'billing_contact', 'business_contact', 'addresses', 'projects'
    ]
    __listing_attributes__ = __summary_attributes__

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', '_customer_user', '_account_manager',
            '_customer_users', '_account_managers', 'business_contact',
            'billing_contact', 'external_id'
        ],
        'overrides': mixins.CustomerBriefyRoles.__colanderalchemy_config__['overrides']
    }

    __raw_acl__ = (
        ('list', ('g:briefy_finance', 'g:briefy_pm', 'g:briefy_bizdev', 'g:system')),
        ('create', ('g:briefy_bizdev', 'g:briefy_finance', 'g:system')),
        ('view', ('g:briefy_finance', 'g:briefy_pm', 'g:briefy_bizdev', 'g:system')),
        ('edit', ('g:briefy_bizdev', 'g:briefy_finance', 'g:system')),
        ('delete', ('g:briefy_finance', 'g:system')),
    )

    parent_customer_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('customers.id'),
        index=True,
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
        backref=orm.backref('customer'),
        lazy='dynamic',
        info={
            'colanderalchemy': {
                'title': 'Billing Addresses',
                'missing': colander.drop,
            }
        }
    )
    """List of Billing Addresses for a Customer

    Returns a collection of :class:`briefy.leica.models.customer.address.CustomerBillingAddress`.
    """

    contacts = orm.relationship(
        'CustomerContact',
        backref=orm.backref('customer'),
        lazy='dynamic',
        info={
            'colanderalchemy': {
                'title': 'Customer Contacts',
                'missing': colander.drop,
            }
        }
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
        info={
            'colanderalchemy': {
                'title': 'Business Contact',
                'default': colander.null,
                'missing': colander.drop,
            }
        }
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
        info={
            'colanderalchemy': {
                'title': 'Billing Contact',
                'default': colander.null,
                'missing': colander.drop,
            }
        }
    )
    """Customer billing contact.

    Returns an instance of :class:`briefy.leica.models.customer.contact.CustomerContact`.
    """

    projects = orm.relationship(
        'Project',
        backref=orm.backref('customer'),
        lazy='dynamic',
        info={
            'colanderalchemy': {
                'title': 'Projects',
                'missing': colander.drop,
            }
        }
    )
    """List of Projects of this Customer.

    Returns a collection of :class:`briefy.leica.models.project.Project`.
    """

    orders = orm.relationship(
        'Order',
        backref=orm.backref('customer'),
        lazy='dynamic',
        info={
            'colanderalchemy': {
                'title': 'Business Contact',
                'missing': colander.drop,
            }
        }
    )
    """List of Orders of this Customer.

    Returns a collection of :class:`briefy.leica.models.job.order.Orders`.
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
        data = super().to_listing_dict()
        data = self._apply_actors_info(data)
        return data

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['slug'] = self.slug
        data['projects'] = [p.to_summary_dict() for p in self.projects]
        add_user_info_to_state_history(self.state_history)
        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data
