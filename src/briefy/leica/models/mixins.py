"""Briefy Leica mixins."""
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import KnackMixin
from briefy.common.db.mixins import BaseBriefyRoles
from briefy.common.db.mixins import LocalRolesMixin
from briefy.common.db.mixins import Mixin
from briefy.common.db.models.roles import LocalRole
from briefy.common.vocabularies.roles import LocalRolesChoices
from briefy.leica.db import Session
from briefy.ws.utils.user import get_public_user_info
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import orm
from sqlalchemy_continuum.utils import count_versions

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class LeicaBriefyRoles(BaseBriefyRoles):
    """Base class for leica local roles."""

    @classmethod
    def get_role_relationship(cls, role_name, viewonly=False, uselist=False):
        return orm.relationship(
            'LocalRole',
            foreign_keys='LocalRole.entity_id',
            viewonly=viewonly,
            uselist=uselist,
            primaryjoin='''and_(
                        LocalRole.entity_id=={entity}.id,
                        LocalRole.entity_type=="{entity}",
                        LocalRole.role_name=="{role_name}"
                    )'''.format(
                entity=cls.__name__,
                role_name=role_name
            )
        )

    @classmethod
    def get_association_proxy(cls, role_name, remote_attr):
        """Get a new association proxy instance."""

        def creator(user_id):
            return cls.create_local_role(user_id, role_name)

        local_attr = '_{role_name}'.format(role_name=role_name)
        return association_proxy(local_attr, remote_attr, creator=creator)

    @classmethod
    def create_local_role(cls, user_id, role_name):
        """Create local LocalRole instance for role and user_id."""
        # TODO: find a way to do this validation here..
        # query = LocalRole.query().filter_by(entity_id=cls.id,
        #                                    user_id=user_id,
        #                                    entity_type=cls.__name__,
        #                                    role_name=role_name)
        # proxy = getattr(cls, role_name)
        # has_users = query.all()
        # if has_users:
        #    raise Exception('User already has local role: {items}'.format(items=has_users))

        return LocalRole(
            entity_id=cls.id,
            user_id=user_id,
            entity_type=cls.__name__,
            role_name=getattr(LocalRolesChoices, role_name)
        )

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

    @declared_attr
    def _customer_user(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of customer_user role_name.
        """
        return cls.get_role_relationship('customer_user')

    @declared_attr
    def customer_user(cls):
        """Return a list of ids of customer users.

        :return: IDs of the customer users.
        """
        return cls.get_association_proxy('customer_user', 'user_id')

    @declared_attr
    def _account_manager(cls) -> list:
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of account_manager role_name.
        """
        return cls.get_role_relationship('account_manager')

    @declared_attr
    def account_manager(cls):
        """Return a list of ids of account manager users.

        :return: IDs of the account manager users.
        """
        return cls.get_association_proxy('account_manager', 'user_id')


class ProjectBriefyRoles(LeicaBriefyRoles):
    """Local roles for the Project context."""

    __actors__ = (
        'customer_user',
        'project_manager',
    )

    @declared_attr
    def _customer_user(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of customer_user role_name.
        """
        return cls.get_role_relationship('customer_user')

    @declared_attr
    def customer_user(cls):
        """Return a list of ids of customer users.

        :return: IDs of the customer users.
        """
        return cls.get_association_proxy('customer_user', 'user_id')

    @declared_attr
    def _project_manager(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of project_manager role_name.
        """
        return cls.get_role_relationship('project_manager')

    @declared_attr
    def project_manager(cls):
        """Return a list of ids of project manager users.

        :return: IDs of the project manager users.
        """
        return cls.get_association_proxy('project_manager', 'user_id')


class OrderBriefyRoles(LeicaBriefyRoles):
    """Local roles for the Order context."""

    __actors__ = (
        'customer_user',
        'project_manager',
        'scout_manager',
    )

    @declared_attr
    def _customer_user(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of customer_user role_name.
        """
        return cls.get_role_relationship('customer_user')

    @declared_attr
    def customer_user(cls):
        """Return a list of ids of customer users.

        :return: IDs of the customer users.
        """
        return cls.get_association_proxy('customer_user', 'user_id')

    @declared_attr
    def _project_manager(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of project_manager role_name.
        """
        return cls.get_role_relationship('project_manager')

    @declared_attr
    def project_manager(cls):
        """Return a list of ids of project manager users.

        :return: IDs of the project manager users.
        """
        return cls.get_association_proxy('project_manager', 'user_id')

    @declared_attr
    def _scout_manager(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of scout_manager role_name.
        """
        return cls.get_role_relationship('scout_manager')

    @declared_attr
    def scout_manager(cls):
        """Return a list of ids of scout manager users.

        :return: IDs of the scout manager users.
        """
        return cls.get_association_proxy('scout_manager', 'user_id')


class AssignmentBriefyRoles(LeicaBriefyRoles):
    """Local roles for the Assignment context."""

    __actors__ = (
        'professional_user',
        'project_manager',
        'scout_manager',
        'qa_manager',
    )

    @declared_attr
    def _professional_user(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of professional_user role_name.
        """
        return cls.get_role_relationship('professional_user')

    @declared_attr
    def professional_user(cls):
        """Return a list of ids of professional users.

        :return: IDs of the professional users.
        """
        return cls.get_association_proxy('professional_user', 'user_id')

    @declared_attr
    def _project_manager(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of project_manager role_name.
        """
        return cls.get_role_relationship('project_manager')

    @declared_attr
    def project_manager(cls):
        """Return a list of ids of project manager users.

        :return: IDs of the project manager users.
        """
        return cls.get_association_proxy('project_manager', 'user_id')

    @declared_attr
    def _scout_manager(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of scout_manager role_name.
        """
        return cls.get_role_relationship('scout_manager')

    @declared_attr
    def scout_manager(cls):
        """Return a list of ids of scout manager users.

        :return: IDs of the scout manager users.
        """
        return cls.get_association_proxy('scout_manager', 'user_id')

    @declared_attr
    def _qa_manager(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of qa_manager role_name.
        """
        return cls.get_role_relationship('qa_manager')

    @declared_attr
    def qa_manager(cls):
        """Return a list of ids of qa manager users.

        :return: IDs of the qa manager users.
        """
        return cls.get_association_proxy('qa_manager', 'user_id')


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
