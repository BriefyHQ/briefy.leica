"""Briefy Leica mixins."""
from briefy.common.db.mixins import BaseBriefyRoles
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import ContactInfoMixin
from briefy.common.db.mixins import KnackMixin
from briefy.common.db.mixins import LocalRolesMixin
from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins import OptIn
from briefy.common.db.mixins import PersonalInfoMixin
from briefy.common.db.models.roles import LocalRole
from briefy.common.vocabularies.roles import LocalRolesChoices
from briefy.common.utils.cache import timeout_cache
from briefy.leica.models.descriptors import LocalRolesGetSetFactory
from briefy.leica.db import Session
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import orm
from sqlalchemy_continuum.utils import count_versions

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils
import uuid


@timeout_cache(600, renew=False)
def get_public_user_info(user_id: str) -> dict:
    """Retrieve user information from briefy.rolleiflex.

    :param user_id: Id for the user we want to query.
    :return: Dictionary with public user information.
    """
    data = {
        'id': user_id,
        'first_name': '',
        'last_name': '',
        'fullname': '',
        'email': '',
        'internal': False,
    }
    from briefy.leica.models import UserProfile
    try:
        _ = uuid.UUID(user_id)  # noqa
    except (ValueError, AttributeError) as exc:
        return data
    else:
        raw_data = UserProfile.get(user_id)
        if raw_data:
            data['id'] = str(raw_data.id)
            data['first_name'] = raw_data.first_name
            data['last_name'] = raw_data.last_name
            data['fullname'] = raw_data.title
            data['email'] = raw_data.email
            data['internal'] = raw_data.internal
        return data


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


class LeicaBriefyRoles(BaseBriefyRoles):
    """Base class for leica local roles."""

    @classmethod
    def get_role_relationship(cls, role_name, viewonly=False, uselist=False):
        """Get Local Role relationship."""
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
    def get_association_proxy(cls, role_name, remote_attr, local_attr=None, permissions=None):
        """Get a new association proxy instance."""
        if not local_attr:
            local_attr = '_{role_name}'.format(role_name=role_name)

        def creator(user_id):
            if isinstance(permissions, dict):
                return cls.create_local_role(user_id, role_name, permissions=permissions)
            else:
                return cls.create_local_role(user_id, role_name)

        getset_factory = LocalRolesGetSetFactory(permissions)
        return association_proxy(
            local_attr,
            remote_attr,
            creator=creator,
            getset_factory=getset_factory
        )

    @classmethod
    def create_local_role(cls, user_id, role_name, permissions=None,
                          entity_type=None, entity_id=None):
        """Create local LocalRole instance for role and user_id."""
        if not entity_type:
            entity_type = cls.__name__
        if not entity_id:
            entity_id = cls.id

        # TODO: this query do not work
        # query = LocalRole.query().filter(
        #      LocalRole.entity_id == entity_id,
        #      LocalRole.user_id == user_id,
        #      LocalRole.entity_type == entity_type,
        #      LocalRole.role_name == role_name
        # )
        # has_user = query.one_or_none()

        payload = dict(
            entity_id=entity_id,
            user_id=user_id,
            entity_type=entity_type,
            role_name=getattr(LocalRolesChoices, role_name),
            can_view=True,
            can_edit=False,
            can_list=False,
            can_delete=False,
            can_create=False,
        )
        if permissions:
            payload.update(permissions)
        result = LocalRole(**payload)
        return result

    def _apply_actors_info(self, data: dict) -> dict:
        """Apply actors information for a given data dictionary.

        :param data: Data dictionary.
        :return: Data dictionary.
        """
        actors = [(k, k) for k in self.__actors__]
        info = self._actors_info()
        for key, attr in actors:
            try:
                value = info.get(attr)
            except (AttributeError, IndexError):
                data[key] = None
            else:
                result = []
                for item in value:
                    user_info = get_public_user_info(item) if item else None
                    result.append(user_info)
                data[key] = result

        return data


class UserProfileBriefyRoles(LeicaBriefyRoles):
    """Local roles for the UserProfile context."""

    __actors__ = (
        'owner',
    )

    __colanderalchemy_config__ = {
        'overrides': {
            'owner': _ID_COLANDER,
        }
    }

    @declared_attr
    def _owner(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of owner role_name.
        """
        return cls.get_role_relationship('owner')

    @declared_attr
    def owner(cls):
        """Return a list of ids with owner local role.

        :return: ID of the owner.
        """
        permissions = dict(
             can_view=True,
             can_edit=True,
             can_list=True,
             can_delete=False,
             can_create=False,
        )
        return cls.get_association_proxy(
            'owner',
            'user_id',
            permissions=permissions
        )


class CustomerBriefyRoles(LeicaBriefyRoles):
    """Local roles for the Customer context."""

    __actors__ = (
        'customer_user',
        'account_manager',
        'customer_users',
        'account_managers',
    )

    __colanderalchemy_config__ = {
        'overrides': {
            'customer_user': _ID_COLANDER,
            'account_manager': _ID_COLANDER,
            'customer_users': _ID_COLANDER_LIST,
            'account_managers': _ID_COLANDER_LIST,
        }
    }

    @declared_attr
    def _customer_user(cls):
        """Relationship: return a list of LocalRoles (deprecated).

        :return: LocalRoles instances of customer_user role_name.
        """
        return cls.get_role_relationship('customer_user')

    @declared_attr
    def customer_user(cls):
        """Return a list of ids of customer users (deprecated).

        :return: IDs of the customer users.
        """
        return cls.get_association_proxy('customer_user', 'user_id')

    @declared_attr
    def _customer_users(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of customer_user role_name.
        """
        return cls.get_role_relationship('customer_user', uselist=True)

    @declared_attr
    def customer_users(cls):
        """Return a list of ids of customer users.

        :return: IDs of the customer users.
        """
        return cls.get_association_proxy(
            'customer_user',
            'user_id',
            local_attr='_customer_users'
        )

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

    @declared_attr
    def _account_managers(cls) -> list:
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of account_manager role_name.
        """
        return cls.get_role_relationship('account_manager', uselist=True)

    @declared_attr
    def account_managers(cls):
        """Return a list of ids of account manager users.

        :return: IDs of the account manager users.
        """
        return cls.get_association_proxy(
            'account_manager',
            'user_id',
            local_attr='_account_managers'
        )


class ProjectBriefyRoles(LeicaBriefyRoles):
    """Local roles for the Project context."""

    __actors__ = (
        'customer_user',
        'project_manager',
        'customer_users',
        'project_managers',
    )

    __colanderalchemy_config__ = {
        'overrides': {
            'customer_user': _ID_COLANDER,
            'project_manager': _ID_COLANDER,
            'customer_users': _ID_COLANDER_LIST,
            'project_managers': _ID_COLANDER_LIST,
        }
    }

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
    def _customer_users(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of customer_user role_name.
        """
        return cls.get_role_relationship('customer_user', uselist=True)

    @declared_attr
    def customer_users(cls):
        """Return a list of ids of customer users.

        :return: IDs of the customer users.
        """
        return cls.get_association_proxy(
            'customer_user',
            'user_id',
            local_attr='_customer_users'
        )

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
    def _project_managers(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of project_manager role_name.
        """
        return cls.get_role_relationship('project_manager', uselist=True)

    @declared_attr
    def project_managers(cls):
        """Return a list of ids of project manager users.

        :return: IDs of the project manager users.
        """
        return cls.get_association_proxy(
            'project_manager',
            'user_id',
            local_attr='_project_managers'
        )


class OrderBriefyRoles(LeicaBriefyRoles):
    """Local roles for the Order context."""

    __actors__ = (
        'customer_user',
        'project_manager',
        'scout_manager',
        'customer_users',
        'project_managers',
        'scout_managers',
    )

    __colanderalchemy_config__ = {
        'overrides': {
            'customer_user': _ID_COLANDER,
            'project_manager': _ID_COLANDER,
            'scout_manager': _ID_COLANDER,
            'customer_users': _ID_COLANDER_LIST,
            'project_managers': _ID_COLANDER_LIST,
            'scout_managers': _ID_COLANDER_LIST,
        }
    }

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
    def _customer_users(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of customer_user role_name.
        """
        return cls.get_role_relationship('customer_user', uselist=True)

    @declared_attr
    def customer_users(cls):
        """Return a list of ids of customer users.

        :return: IDs of the customer users.
        """
        return cls.get_association_proxy(
            'customer_user',
            'user_id',
            local_attr='_customer_users'
        )

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
    def _project_managers(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of project_manager role_name.
        """
        return cls.get_role_relationship('project_manager', uselist=True)

    @declared_attr
    def project_managers(cls):
        """Return a list of ids of project manager users.

        :return: IDs of the project manager users.
        """
        return cls.get_association_proxy(
            'project_manager',
            'user_id',
            local_attr='_project_managers'
        )

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
    def _scout_managers(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of scout_manager role_name.
        """
        return cls.get_role_relationship('scout_manager', uselist=True)

    @declared_attr
    def scout_managers(cls):
        """Return a list of ids of scout manager users.

        :return: IDs of the scout manager users.
        """
        return cls.get_association_proxy(
            'scout_manager',
            'user_id',
            local_attr='_scout_managers'
        )


class AssignmentBriefyRoles(LeicaBriefyRoles):
    """Local roles for the Assignment context."""

    __actors__ = (
        'professional_user',
        'project_manager',
        'scout_manager',
        'qa_manager',
        'professional_users',
        'project_managers',
        'scout_managers',
        'qa_managers',
    )

    __colanderalchemy_config__ = {
        'overrides': {
            'professional_user': _ID_COLANDER,
            'project_manager': _ID_COLANDER,
            'scout_manager': _ID_COLANDER,
            'qa_manager': _ID_COLANDER,
            'professional_users': _ID_COLANDER_LIST,
            'project_managers': _ID_COLANDER_LIST,
            'scout_managers': _ID_COLANDER_LIST,
            'qa_managers': _ID_COLANDER_LIST,
        }
    }

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
        permissions = dict(
             can_view=True,
             can_edit=True,
             can_list=True,
             can_delete=False,
             can_create=False,
        )
        return cls.get_association_proxy(
            'professional_user',
            'user_id',
            permissions=permissions
        )

    @declared_attr
    def _professional_users(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of professional_user role_name.
        """
        return cls.get_role_relationship('professional_user', uselist=True)

    @declared_attr
    def professional_users(cls):
        """Return a list of ids of professional users.

        :return: IDs of the professional users.
        """
        permissions = dict(
             can_view=True,
             can_edit=True,
             can_list=True,
             can_delete=False,
             can_create=False,
        )
        return cls.get_association_proxy(
            'professional_user',
            'user_id',
            local_attr='_professional_users',
            permissions=permissions
        )

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
    def _project_managers(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of project_manager role_name.
        """
        return cls.get_role_relationship('project_manager', uselist=True)

    @declared_attr
    def project_managers(cls):
        """Return a list of ids of project manager users.

        :return: IDs of the project manager users.
        """
        return cls.get_association_proxy(
            'project_manager',
            'user_id',
            local_attr='_project_managers'
        )

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
    def _scout_managers(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of scout_manager role_name.
        """
        return cls.get_role_relationship('scout_manager', uselist=True)

    @declared_attr
    def scout_managers(cls):
        """Return a list of ids of scout manager users.

        :return: IDs of the scout manager users.
        """
        return cls.get_association_proxy(
            'scout_manager',
            'user_id',
            local_attr='_scout_managers'
        )

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

    @declared_attr
    def _qa_managers(cls):
        """Relationship: return a list of LocalRoles.

        :return: LocalRoles instances of qa_manager role_name.
        """
        return cls.get_role_relationship('qa_manager', uselist=True)

    @declared_attr
    def qa_managers(cls):
        """Return a list of ids of qa manager users.

        :return: IDs of the qa manager users.
        """
        return cls.get_association_proxy(
            'qa_manager',
            'user_id',
            local_attr='_qa_managers'
        )


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

    reason_additional_compensation = sa.Column(
        sa.Text(),
        nullable=True,
        default='',
        info={
            'colanderalchemy': {
                'title': 'Type of Set',
                'default': '',
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
        """Explicitly sets a version to the asset (Deprecated).

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


class UserProfileMixin(ContactInfoMixin, PersonalInfoMixin, OptIn, KLeicaVersionedMixin):
    """A user profile on our system."""

    pass
