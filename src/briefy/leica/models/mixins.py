"""Briefy Leica mixins."""
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import KnackMixin
from briefy.common.db.mixins import LocalRolesMixin
from briefy.common.db.mixins import Mixin
from briefy.leica.db import Session
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_continuum.utils import count_versions

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class AssignmentFinancialInfo:
    """Mixin containing financial information of a jobAssignment."""

    # Photographer Payout
    payout_currency = sa.Column(
        sautils.CurrencyType,
        default='EUR'
    )
    """Professional Payout currency.

    ISO4217 code for the currency to be used to payout the professional.
    """

    payout_value = sa.Column(
        sa.Integer,
        nullable=False,
        default=0,
        info={
            'colanderalchemy': {
                'title': 'Photographer Payout',
                'missing': None,
                'typ': colander.Integer
            }
        }
    )
    """Professional Payout value.

    How much the professional will be paid for this Job.
    This value is expressed in cents.
    """

    # Photographer Expenses
    travel_expenses = sa.Column(
        sa.Integer,
        nullable=False,
        default=0,
        info={
            'colanderalchemy': {
                'title': 'Travel Expenses',
                'missing': None,
                'typ': colander.Integer
            }
        }
    )
    """Travel expenses amount.

    Amount to be paid to the professional as travel expenses.
    This value is expressed in cents.
    """

    additional_compensation = sa.Column(
        sa.Integer,
        nullable=False,
        default=0,
        info={
            'colanderalchemy': {
                'title': 'Additional Compensation',
                'missing': None,
                'typ': colander.Integer
            }
        }
    )
    """Amount of additional (extra) compensation.

    Amount to be paid to the professional as additional compensation.
    This value is expressed in cents.
    """

    payable = sa.Column(
        sa.Boolean,
        nullable=False,
        default=True,
        info={
            'colanderalchemy': {
                'title': 'Is this Assignment Payable?',
                'missing': True,
                'typ': colander.Boolean
            }
        }
    )
    """Payout should be payable or not?.

    By default all assignments should be paid but there are exceptions to this when a customer
    rejects a Job and we have to reassign it to a new Professional.
    """

    @hybrid_property
    def costs(self) -> int:
        """Sum of costs for this job.

        :return: Return the sum of costs, in cents, of this job.
        """
        return self.payout_value + self.travel_expenses + self.additional_compensation


class OrderFinancialInfo:
    """Mixin containing financial information of a JobOrder."""

    # Set price
    price_currency = sa.Column(
        sautils.CurrencyType,
        default='EUR'
    )
    """Price currency.

    ISO4217 code for the currency to be used by customer to pay Briefy.
    """

    _price = sa.Column(
        'price',
        sa.Integer,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Set Price',
                'missing': None,
                'typ': colander.Integer
            }
        }
    )
    """Price to be paid, by the customer, for this job.

    Amount to be paid by the customer for this job.
    This value is expressed in cents.
    """

    @property
    def price(self) -> int:
        """Price of this job.

        :return: Return the price, in cents, of this job.
        """
        return self._price


class VersionMixin:
    """Versioning support for Leica objects."""

    __versioned__ = {
        'exclude': ['state_history', '_state_history', ]
    }
    """SQLAlchemy Continuum settings.

    By default we do not keep track of state_history.
    """

    @property
    def version(self) -> int:
        """Return the current version number.

        We are civilised here, so version numbering starts from zero ;-)
        :return: Version number of this object.
        """
        versions = count_versions(self)
        return versions - 1

    @version.setter
    def version(self, value: int) -> int:
        """Explicitly sets a version to the asset. (Deprecated)

        XXX: Here only to avoid issues if any client tries to set this.
        :param value:
        """
        pass


class LeicaMixin(LocalRolesMixin, Mixin):
    """Base  mixin for Leica objects."""

    __session__ = Session

    @declared_attr
    def __tablename__(cls):
        """Return tablename.

        Tablename, by our convention, is always the plural of the lowercase version of the
        class name.
        """
        tablename = '{klass}s'.format(
            klass=cls.__name__.lower()
        )
        return tablename


class LeicaVersionedMixin(VersionMixin, BaseMetadata, LeicaMixin):
    """Base mixin for Leica Objects supporting versioning.

    Used on objects that require Version support and Base metadata.
    """

    pass


class KLeicaVersionedMixin(KnackMixin, LeicaVersionedMixin):
    """Base mixin for Leica Objects with Knack support.

    Used on objects that require Version support, Base metadata amd Knack integration.
    """

    pass


class PolaroidMixin:
    """Mixin to handle Polaroid integration."""

    pass
