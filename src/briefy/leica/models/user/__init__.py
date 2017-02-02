"""User profile information."""
from briefy.common.vocabularies.roles import LocalRolesChoices
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models import Customer
from briefy.leica.models import LocalRole
from briefy.leica.models.user import workflows
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import UUIDType

import colander
import copy
import sqlalchemy as sa


__colander_alchemy_config_overrides__ = \
    copy.copy(mixins.UserProfileBriefyRoles.__colanderalchemy_config__['overrides'])

__colander_alchemy_config_overrides__.update(
    {
        'description': {
            'title': 'Description',
            'missing': colander.drop,
            'typ': colander.String()
        },
        'customer_roles': {
            'title': 'Customer Roles',
            'missing': colander.drop,
            'typ': colander.String()
        },
    }
)


class UserProfile(mixins.UserProfileMixin, mixins.UserProfileBriefyRoles, Base):
    """A Professional on our system."""

    __tablename__ = 'userprofiles'

    _workflow = workflows.UserProfileWorkflow

    __summary_attributes__ = [
        'id', 'title', 'description', 'created_at', 'updated_at', 'state',
        'email', 'mobile', 'type', 'slug'
    ]

    __summary_attributes_relations__ = []

    __listing_attributes__ = __summary_attributes__

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'type', 'external_id', '_owner', '_customer_roles'
        ],
        'overrides': __colander_alchemy_config_overrides__
    }

    id = sa.Column(
        UUIDType(),
        unique=True,
        primary_key=True,
        info={'colanderalchemy': {
              'title': 'User id',
              'validator': colander.uuid,
              'missing': colander.drop,
              'typ': colander.String}}
    )

    type = sa.Column(sa.String(50))
    """Polymorphic type."""

    @declared_attr
    def __mapper_args__(cls):
        """Return polymorphic identity."""
        cls_name = cls.__name__.lower()
        args = {
            'polymorphic_identity': cls_name,
        }
        if cls_name == 'userprofile':
            args['polymorphic_on'] = cls.type
        return args

    @hybrid_property
    def user_id(self):
        """User id."""
        return self.id

    @declared_attr
    def title(cls):
        """Return the User fullname."""
        return sa.orm.column_property(cls.first_name + " " + cls.last_name)


class CustomerUserProfile(UserProfile):
    """A Customer on our system."""

    __tablename__ = 'customeruserprofiles'

    __raw_acl__ = (
        ('create', ('g:briefy_bizdev', 'g:briefy_finance', 'g:briefy_pm', 'g:system')),
        ('list', ('g:briefy', 'g:system')),
        ('view', ('g:briefy', 'g:system')),
        ('edit', ('g:briefy_bizdev', 'g:briefy_finance', 'g:briefy_pm', 'g:system')),
        ('delete', ('g:briefy_finance', 'g:system')),
    )

    id = sa.Column(
        UUIDType(),
        sa.ForeignKey('userprofiles.id'),
        unique=True,
        primary_key=True,
        info={'colanderalchemy': {
              'title': 'User id',
              'validator': colander.uuid,
              'missing': colander.drop,
              'typ': colander.String}}
    )

    @declared_attr
    def customer_ids(cls):
        """Return a list of customer ids related to this CustomerUserProfile."""
        return association_proxy('_customer_roles', 'entity_id')

    @declared_attr
    def _customer_roles(cls):
        """Local roles of this user in the Customer context as customer_user."""
        return sa.orm.relationship(
            'LocalRole',
            foreign_keys='LocalRole.user_id',
            viewonly=True,
            uselist=True,
            primaryjoin='''and_(
                        LocalRole.user_id == CustomerUserProfile.id,
                        LocalRole.entity_type=="{entity}",
                        LocalRole.role_name=="{role_name}"
                    )'''.format(
                entity='Customer',
                role_name='customer_user',
            )
        )

    @property
    def customer_roles(self):
        """Return roles related to this customer user profile."""
        return self._customer_roles

    @customer_roles.setter
    def customer_roles(self, customer_id):
        """Add customer_user role for this customer user profile."""
        customer = Customer.get(customer_id)
        if not customer:
            raise ValueError('Invalid customer ID')
        if not self.id:
            return
        if self.id not in customer.customer_users:
            customer.customer_users.append(self.id)


class BriefyUserProfile(UserProfile):
    """A Briefy user on our system."""

    __tablename__ = 'briefyuserprofiles'

    __raw_acl__ = (
        ('create', ('g:briefy_finance', 'g:briefy_tech', 'g:system')),
        ('list', ('g:briefy', 'g:system')),
        ('view', ('g:briefy', 'g:system')),
        ('edit', ('g:briefy_finance', 'g:briefy_tech', 'g:system')),
        ('delete', ('g:briefy_finance', 'g:system')),
    )

    id = sa.Column(
        UUIDType(),
        sa.ForeignKey('userprofiles.id'),
        unique=True,
        primary_key=True,
        info={'colanderalchemy': {
              'title': 'User id',
              'validator': colander.uuid,
              'missing': colander.drop,
              'typ': colander.String}}
    )
