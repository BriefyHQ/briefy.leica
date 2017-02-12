"""User profile information."""
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models import Customer
from briefy.leica.models.user import workflows
from briefy.leica.utils.user import add_user_info_to_state_history
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import UUIDType
from uuid import UUID

import colander
import copy
import sqlalchemy as sa


__colander_alchemy_config_overrides__ = \
    copy.copy(mixins.UserProfileBriefyRoles.__colanderalchemy_config__['overrides'])

__colander_alchemy_config_overrides__.update(
    {
        'customer_roles': {
            'title': 'Customer Roles',
            'missing': colander.drop,
            'typ': colander.String()
        },
        'project_roles': {
            'title': 'Project Roles',
            'missing': colander.drop,
            'typ': colander.List()
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
            'state_history', 'state', 'type', 'external_id', '_owner', '_customer_roles',
            '_project_roles'

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

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        add_user_info_to_state_history(self.state_history)
        return data


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
        index=True,
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
        id_ = self.id
        if not customer:
            raise ValueError('Invalid customer ID')
        if not id_:
            return
        if isinstance(id_, str):
            id_ = UUID(id_)
        if id_ not in customer.customer_users:
            customer.customer_users.append(id_)

    @declared_attr
    def project_ids(cls):
        """Return a list of project ids related to this CustomerUserProfile."""
        return association_proxy('_project_roles', 'entity_id')

    @declared_attr
    def _project_roles(cls):
        """Local roles of this user in the Customer context as project_user."""
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
                entity='Project',
                role_name='customer_users',
            )
        )

    @property
    def project_roles(self):
        """Return roles related to this project user profile."""
        return self._project_roles

    @project_roles.setter
    def project_roles(self, project_ids):
        """Add project_user role for this project user profile."""
        from briefy.leica.models import Project

        for project_id in project_ids:
            project = Project.get(project_id)
            id_ = self.id
            if not project:
                raise ValueError('Invalid project ID')
            if not id_:
                return
            if isinstance(id_, str):
                id_ = UUID(id_)
            if id_ not in project.customer_users:
                project.customer_users.append(id_)



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
        index=True,
        unique=True,
        primary_key=True,
        info={'colanderalchemy': {
              'title': 'User id',
              'validator': colander.uuid,
              'missing': colander.drop,
              'typ': colander.String}}
    )
