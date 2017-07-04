"""Briefy Leica mixins."""
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import ContactInfoMixin
from briefy.common.db.mixins import KnackMixin
from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins import OptIn
from briefy.common.db.mixins import PersonalInfoMixin
from briefy.common.db.mixins import SubItemMixin
from briefy.common.db.mixins import VersionMixin
from briefy.common.utilities.interfaces import IUserProfileQuery
from briefy.common.utils import schema
from briefy.common.utils.cache import timeout_cache
from briefy.leica.db import Session
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from zope.component import getUtility

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


@timeout_cache(600, renew=False)
def get_public_user_info(user_id: str) -> dict:
    """Retrieve user information from briefy.rolleiflex.

    :param user_id: Id for the user we want to query.
    :return: Dictionary with public user information.
    """
    profile_service = getUtility(IUserProfileQuery)
    return profile_service.get_data(user_id)


_ID_COLANDER = {
    'title': 'ID',
    'validator': colander.uuid,
    'missing': colander.drop,
    'typ': colander.String()
}

_ID_COLANDER_LIST = {
    'title': 'List of IDs',
    'missing': colander.drop,
    'typ': colander.List()
}


class UserProfileRolesMixin:
    """Local roles for the UserProfile context."""

    __actors__ = (
        'owner',
    )

    __colanderalchemy_config__ = {
        'overrides': {
            'owner': _ID_COLANDER,
        }
    }


class CustomerRolesMixin:
    """Local roles for the Customer context."""

    __actors__ = (
        'customer_manager',
        'customer_pm',
        'customer_qa',
        'internal_account',
    )

    __colanderalchemy_config__ = {
        'overrides': {
            'customer_manager': _ID_COLANDER_LIST,
            'customer_pm': _ID_COLANDER_LIST,
            'customer_qa': _ID_COLANDER_LIST,
            'internal_account': _ID_COLANDER_LIST,
        }
    }


class ProjectRolesMixin:
    """Local roles for the Project context."""

    __actors__ = (
        'internal_qa',
        'internal_pm',
        'internal_scout',
        'project_customer_pm',
        'project_customer_qa',
    )

    __colanderalchemy_config__ = {
        'overrides': {
            'internal_qa': _ID_COLANDER_LIST,
            'internal_pm': _ID_COLANDER_LIST,
            'internal_scout': _ID_COLANDER_LIST,
            'project_customer_pm': _ID_COLANDER_LIST,
            'project_customer_qa': _ID_COLANDER_LIST,
        }
    }


class OrderRolesMixin:
    """Local roles for the Order context."""

    __actors__ = (
        'order_customer_qa',
    )

    __colanderalchemy_config__ = {
        'overrides': {
            'order_customer_qa': _ID_COLANDER_LIST,
        }
    }


class AssignmentRolesMixin:
    """Local roles for the Assignment context."""

    __actors__ = (
        'professional_user',
        'assignment_internal_scout',
        'assignment_internal_qa',
    )

    __colanderalchemy_config__ = {
        'overrides': {
            'professional_user': _ID_COLANDER_LIST,
            'assignment_internal_scout': _ID_COLANDER_LIST,
            'assignment_internal_qa': _ID_COLANDER_LIST,
        }
    }


class ProfessionalPayoutInfo:
    """Professional payout information."""

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


class AssignmentFinancialInfo(ProfessionalPayoutInfo):
    """Mixin containing financial information of a Assignment."""

    # Photographer Expenses
    travel_expenses = sa.Column(
        sa.Integer,
        nullable=False,
        default=0,
        info={
            'colanderalchemy': {
                'title': 'Travel Expenses',
                'default': 0,
                'missing': colander.drop,
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
                'default': 0,
                'missing': colander.drop,
                'typ': colander.Integer
            }
        }
    )
    """Amount of additional (extra) compensation.

    Amount to be paid to the professional as additional compensation.
    This value is expressed in cents.
    """

    reason_additional_compensation = sa.Column(
        sa.Text(),
        nullable=True,
        default=None,
        info={
            'colanderalchemy': {
                'title': 'Type of Set',
                'default': None,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Reason for Additional Compensation.

    Text explaining why we give an additional compensation to the Professional.
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
    """Mixin containing financial information of an Order."""

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
    """Order Price as stated on the agreement with the customer.

    Default amount to be applied to this order.
    This value is expressed in cents.
    """

    @hybrid_property
    def price(self) -> int:
        """Order Price as stated on the agreement with the customer.

        :return: Return the price, in cents, of this order.
        """
        return self._price

    @price.setter
    def price(self, value: int):
        """Order Price of this job.

        :value: Price, in cents, of this order.
        """
        self._price = value


class BaseLeicaMixin:
    """Base mixin for all leica models."""

    __session__ = Session

    def _apply_actors_info(self, data: dict) -> dict:
        """Add actors info to data payload.

        :param data: payload with all data from a model
        :return: Dictionary with data payload updated.
        """
        profile_service = getUtility(IUserProfileQuery)
        return profile_service.apply_actors_info(data, self.__actors__)

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


class LeicaMixin(BaseLeicaMixin, Mixin):
    """Base  mixin for Leica objects."""


class LeicaSubMixin(BaseLeicaMixin, SubItemMixin):
    """Base mixin for Leica sub Item objects.

    This includes versionnig and metadata in the Item base table.
    """


class LeicaSubVersionedMixin(VersionMixin, LeicaSubMixin):
    """Base mixin for Leica Objects supporting versioning and sub item of Item.

    Used on objects that require Version support and Base metadata.
    """

    pass


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


class UserProfileMixin(ContactInfoMixin, PersonalInfoMixin, OptIn, LeicaSubVersionedMixin):
    """A user profile on our system."""

    email = sa.Column(
        sautils.types.EmailType(),
        nullable=True,
        unique=True,
        info={
            'colanderalchemy': {
                'title': 'Email',
                'default': '',
                'typ': colander.String
            }
        }
    )
    """Email of the contact person."""


class TaxInfo:
    """Tax information (DEPRECATED)."""

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


class BillingAddress:
    """BillingAddress information.

    This mixin provides a simplified structure to deal with billing addresses
    """

    billing_address = sa.Column(
        JSONB,
        info={
            'colanderalchemy': {
                'typ': schema.JSONType
            }
        }
    )
    """Structure containing address information.

    Info expected schema::

        {
          'additional_info': 'House 3, Entry C, 1st. floor, c/o GLG',
          'formatted_address': 'Schlesische Straße 27, Kreuzberg, Berlin, 10997, DE',
          'place_id': 'ChIJ8-exwVNOqEcR8hBPr-VUmdQ',
          'province': 'Berlin',
          'locality': 'Berlin',
          'sublocality': 'Kreuzberg',
          'route': 'Schlesische Straße',
          'street_number': '27',
          'country': 'DE',
          'postal_code': '10997'
        }

    Ref: https://maps-apis.googleblog.com/2016/11/address-geocoding-in-google-maps-apis.html
    """
