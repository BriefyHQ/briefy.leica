"""Briefy Leica mixins."""
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import KnackMixin
from briefy.common.db.mixins import Mixin
from briefy.leica.db import Session
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_continuum.utils import count_versions

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class JobFinancialInfo:
    """Mixin containing financial information of a job."""

    # Photographer Payout
    payout_currency = sa.Column(
        sautils.CurrencyType,
        default='EUR'
    )
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

    # Set price
    price_currency = sa.Column(
        sautils.CurrencyType,
        default='EUR'
    )
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

    @property
    def price(self) -> int:
        """Price of this job.

        :return: Return the price, in cents, of this job.
        """
        return self._price

    @hybrid_property
    def costs(self) -> int:
        """Sum costs for this job.

        :return: Return the sum of costs, in cents, of this job.
        """
        return self.payout_value + self.travel_expenses + self.additional_compensation


class VersionMixin:
    """Versioning support for Leica objects."""

    __versioned__ = {
        'exclude': ['state_history', '_state_history', ]
    }

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


class LeicaMixin(Mixin):
    """Base  mixin for Leica objects."""

    __session__ = Session

    @declared_attr
    def __tablename__(cls):
        """Return tablename."""
        tablename = '{klass}s'.format(
            klass=cls.__name__.lower()
        )
        return tablename


class LeicaVersionedMixin(VersionMixin, BaseMetadata, LeicaMixin):
    """Base mixin for Leica Objects."""

    pass


class KLeicaVersionedMixin(KnackMixin, LeicaVersionedMixin):
    """Base mixin for Leica Objects with Knack support."""

    pass
