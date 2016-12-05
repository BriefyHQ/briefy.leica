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
class Customer(TaxInfo, mixins.PolaroidMixin, mixins.KLeicaVersionedMixin, Base):
    """A Customer for Briefy."""

    _workflow = workflows.CustomerWorkflow

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', '_slug']}

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
        lazy='dynamic'
    )
    """List of Billing Addresses for a Customer

    Returns a collection of :class:`briefy.leica.models.customer.addrees.CustomerBillingAddress`.
    """

    projects = orm.relationship(
        'Project',
        backref=orm.backref('customer', lazy='joined'),
        lazy='dynamic'
    )
    """List of Projects of this Customer.

    Returns a collection of :class:`briefy.leica.models.project.Project`.
    """

    jobs = orm.relationship(
        'Job',
        backref=orm.backref('customer', lazy='joined'),
        lazy='dynamic'
    )
    """List of Jobs of this Customer.

    Returns a collection of :class:`briefy.leica.models.job.Job`.
    """

    @declared_attr
    def _external_model_(cls):
        """Name of the model on Knack."""
        return 'Company'

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        add_user_info_to_state_history(self.state_history)
        return data