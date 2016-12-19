"""Briefy Leica mixins."""
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import KnackMixin
from briefy.common.db.mixins import BaseBriefyRoles
from briefy.common.db.mixins import LocalRolesMixin
from briefy.common.db.mixins import Mixin
from briefy.leica.db import Session
from briefy.ws.utils.user import get_public_user_info
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_continuum.utils import count_versions

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class LeicaBriefyRoles(BaseBriefyRoles):
    """Base class for leica local roles."""

    def _apply_actors_info(self, data: dict) -> dict:
        """Apply actors information for a given data dictionary.

        :param data: Data dictionary.
        :return: Data dictionary.
        """
        actors = [(k, k) for k in self.__actors__]
        info = self._actors_info()
        for key, attr in actors:
            try:
                value = info.get(attr).pop()
            except (AttributeError, IndexError):
                data[key] = None
            else:
                data[key] = get_public_user_info(value) if value else None
        return data


class CustomerBriefyRoles(LeicaBriefyRoles):
    """Local roles for the Customer context."""

    __actors__ = (
        'customer_user',
        'account_manager',
    )

    @property
    def customer_user(self) -> list:
        """Return a list of ids of customer users.

        :return: IDs of the customer users.
        """
        roles = self.local_roles
        return self._filter_lr_by_name(roles, 'customer_user')

    @customer_user.setter
    def customer_user(self, user_id: str) -> None:
        """Set a new customer_user for this object.

        :param user_id: ID of the customer_user.
        """
        self._add_local_role_user_id(user_id, 'customer_user')

    @property
    def account_manager(self) -> list:
        """Return a list of ids of account_manager.

        :return: IDs of the account_manager.
        """
        roles = self.local_roles
        return self._filter_lr_by_name(roles, 'account_manager')

    @account_manager.setter
    def account_manager(self, user_id: str) -> None:
        """Set a new account_manager for this object.

        :param user_id: IDs of the account_manager.
        """
        self._add_local_role_user_id(user_id, 'account_manager')


class ProjectBriefyRoles(LeicaBriefyRoles):
    """Local roles for the Project context."""

    __actors__ = (
        'customer_user',
        'project_manager',
    )

    @property
    def customer_user(self) -> list:
        """Return a list of ids of customer users.

        :return: IDs of the customer users.
        """
        roles = self.local_roles
        return self._filter_lr_by_name(roles, 'customer_user')

    @customer_user.setter
    def customer_user(self, user_id: str) -> None:
        """Set a new customer_user for this object.

        :param user_id: ID of the customer_user.
        """
        self._add_local_role_user_id(user_id, 'customer_user')

    @property
    def project_manager(self) -> list:
        """Return a list of ids of project_manager.

        :return: IDs of the project_manager.
        """
        roles = self.local_roles
        return self._filter_lr_by_name(roles, 'project_manager')

    @project_manager.setter
    def project_manager(self, user_id: str) -> None:
        """Set a new project_manager for this object.

        :param user_id: IDs of the project_manager.
        """
        self._add_local_role_user_id(user_id, 'project_manager')


class OrderBriefyRoles(ProjectBriefyRoles):
    """Local roles for the Order context."""

    __actors__ = (
        'customer_user',
        'project_manager',
        'scout_manager',
    )

    @property
    def scout_manager(self) -> list:
        """Return a list of ids of scout_managers.

        :return: ID of the scout_manager.
        """
        roles = self.local_roles
        return self._filter_lr_by_name(roles, 'scout_manager')

    @scout_manager.setter
    def scout_manager(self, user_id: str) -> None:
        """Set a new scout_manager for this object.

        :param user_id: ID of the scout_manager.
        """
        self._add_local_role_user_id(user_id, 'scout_manager')


class AssignmentBriefyRoles(LeicaBriefyRoles):
    """Local roles for the Assignment context."""

    __actors__ = (
        'professional_id',
        'project_manager',
        'scout_manager',
        'qa_manager',
    )

    @property
    def project_manager(self) -> list:
        """Return a list of ids of project managers.

        :return: ID of the project_manager.
        """
        roles = self.local_roles
        return self._filter_lr_by_name(roles, 'project_manager')

    @project_manager.setter
    def project_manager(self, user_id: str) -> None:
        """Set a new project_manager for this object.

        :param user_id: ID of the project_manager.
        """
        self._add_local_role_user_id(user_id, 'project_manager')

    @property
    def qa_manager(self) -> list:
        """Return a list of ids of qa_managers.

        :return: ID of the qa_manager.
        """
        roles = self.local_roles
        return self._filter_lr_by_name(roles, 'qa_manager')

    @qa_manager.setter
    def qa_manager(self, user_id: str) -> None:
        """Set a new qa_manager for this object.

        :param user_id: ID of the qa_manager.
        """
        self._add_local_role_user_id(user_id, 'qa_manager')

    @property
    def scout_manager(self) -> list:
        """Return a list of ids of scout_managers.

        :return: ID of the scout_manager.
        """
        roles = self.local_roles
        return self._filter_lr_by_name(roles, 'scout_manager')

    @scout_manager.setter
    def scout_manager(self, user_id: str) -> None:
        """Set a new scout_manager for this object.

        :param user_id: ID of the scout_manager.
        """
        self._add_local_role_user_id(user_id, 'scout_manager')

    def _apply_actors_info(self, data: dict) -> dict:
        """Apply actors information for a given data dictionary.

        :param data: Data dictionary.
        :return: Data dictionary.
        """
        actors = [(k, k) for k in self.__actors__]
        info = self._actors_info()
        for key, attr in actors:
            key = key if key != 'professional_id' else 'professional'
            try:
                value = info.get(attr).pop()
            except (AttributeError, IndexError):
                data[key] = None
            else:
                data[key] = get_public_user_info(value) if value else None
        return data


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
    """Mixin containing financial information of a jobAssignment."""

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

    @hybrid_property
    def price(self) -> int:
        """Price of this job.

        :return: Return the price, in cents, of this job.
        """
        return self._price

    @price.setter
    def price(self, value: int):
        """Set Price of this job.

        :return: Set the price, in cents, of this job.
        """
        self._price = value


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
