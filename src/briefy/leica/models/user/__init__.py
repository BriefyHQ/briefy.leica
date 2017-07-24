"""User profile information."""
from briefy.common.db.mixins.local_roles import set_local_roles_by_principal
from briefy.common.db.models import Item
from briefy.common.db.models.local_role import LocalRole
from briefy.common.utils import schema
from briefy.leica.models import Customer
from briefy.leica.models import mixins
from briefy.leica.models.user import workflows
from briefy.leica.utils.user import add_user_info_to_state_history
from collections import defaultdict
from copy import deepcopy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import UUIDType

import colander
import copy
import sqlalchemy as sa
import sqlalchemy_utils as sautils


__colander_alchemy_config_overrides__ = \
    copy.copy(mixins.UserProfileRolesMixin.__colanderalchemy_config__['overrides'])

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


class UserProfile(mixins.UserProfileMixin, mixins.UserProfileRolesMixin, Item):
    """A Professional on our system."""

    __tablename__ = 'userprofiles'

    _workflow = workflows.UserProfileWorkflow

    __summary_attributes__ = [
        'id', 'title', 'description', 'created_at', 'updated_at', 'state',
        'email', 'mobile', 'type', 'slug', 'fullname'
    ]

    __summary_attributes_relations__ = []

    __listing_attributes__ = __summary_attributes__ + ['internal', 'company_name']

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'type', '_owner',

        ],
        'overrides': __colander_alchemy_config_overrides__
    }

    messengers = sa.Column(
        'messengers',
        JSONB,
        default=None,
        info={
            'colanderalchemy': {
                'title': 'Messenger contact information',
                'missing': colander.drop,
                'typ': schema.JSONType
            }
        }
    )
    """Messenger applications used by this person."""

    @hybrid_property
    def user_id(self):
        """User id."""
        return self.id

    @hybrid_property
    def title(self):
        """Return the User fullname."""
        return self.fullname

    @title.setter
    def title(self, value: str):
        """Set the User fullname."""
        raise ValueError(
            'You can not set the user profile title. Please update first_name and last_name.'
        )

    @title.expression
    def title(cls):
        """Return the User fullname."""
        return cls.first_name + ' ' + cls.last_name

    @sautils.observes('first_name', 'last_name')
    def _title_observer(self, first_name, last_name):
        """Calculate dates on a change of a state."""
        self._title = first_name + ' ' + last_name

    def to_dict(self, excludes: list=None, includes: list=None):
        """Return a dict representation of this object."""
        data = super().to_dict(excludes=excludes, includes=includes)
        add_user_info_to_state_history(self.state_history)
        return data


class CustomerUserProfile(UserProfile):
    """A Customer on our system."""

    __tablename__ = 'customeruserprofiles'

    _workflow = workflows.CustomerUserProfileWorkflow

    __summary_attributes__ = UserProfile.__summary_attributes__.copy() + [
        'customer_roles',  'project_roles',
    ]

    __listing_attributes__ = __summary_attributes__ + [
        'internal', 'company_name',
    ]

    __raw_acl__ = (
        ('create', ('g:briefy_bizdev', 'g:briefy_finance', 'g:briefy_pm', 'g:system')),
        ('list', ('g:briefy', 'g:system')),
        ('view', ('g:briefy', 'g:system')),
        ('edit', ('g:briefy_bizdev', 'g:briefy_finance', 'g:briefy_pm', 'g:system')),
        ('delete', ('g:briefy_finance', 'g:system')),
    )

    __colanderalchemy_config__ = {
        'overrides': {
                'customer_roles': {
                    'title': 'User roles in the customer',
                    'default': '',
                    'missing': colander.drop,
                    'typ': colander.List()
                },
                'project_roles': {
                    'title': 'User roles in the projects',
                    'default': '',
                    'missing': colander.drop,
                    'typ': colander.Mapping()
                },
        }
    }

    id = sa.Column(
        UUIDType(),
        sa.ForeignKey('userprofiles.id'),
        index=True,
        unique=True,
        primary_key=True,
        info={
            'colanderalchemy': {
                'title': 'User ID',
                'validator': colander.uuid,
                'missing': colander.drop,
                'typ': colander.String()
            }
        }
    )

    customer_id = sa.Column(
        UUIDType(),
        sa.ForeignKey('customers.id'),
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Customer ID',
                'validator': colander.uuid,
                'missing': colander.drop,
                'typ': colander.String()
            }
        }
    )

    @classmethod
    def create(cls, payload) -> object:
        """Factory that creates a new instance of this object.

        :param payload: Dictionary containing attributes and values
        :type payload: dict
        """
        payload = deepcopy(payload)
        project_roles = payload.pop('project_roles')
        customer_roles = payload.pop('customer_roles')
        obj = super().create(payload)
        setattr(obj, 'project_roles', project_roles)
        setattr(obj, 'customer_roles', customer_roles)
        return obj

    @hybrid_property
    def customer(self):
        """Customer object this user belongs."""
        return Customer.get(self.customer_id)

    @property
    def _customer_roles(self):
        """Get customer roles for this user in the customer context."""
        customer = Customer.get(self.customer_id)
        return {r.role_name for r in customer.local_roles if r.principal_id == self.id}

    @hybrid_property
    def customer_roles(self):
        """Return roles related to this customer user profile."""
        return list(self._customer_roles)

    @customer_roles.setter
    def customer_roles(self, roles: list):
        """Add customer_user role for this customer user profile."""
        customer = self.customer
        set_local_roles_by_principal(customer, self.id, roles)

    @hybrid_property
    def project_ids(self):
        """Return a list of project ids related to the customer the user belongs."""
        roles = LocalRole.query().filter(
            LocalRole.item_type == 'Project',
            LocalRole.principal_id == self.id
        )
        return [lr.item_id for lr in roles]

    @hybrid_property
    def _project_roles(self):
        """Local roles of this user in the Customer context as project_user."""
        roles = LocalRole.query().filter(
            LocalRole.item_type == 'Project',
            LocalRole.principal_id == self.id
        )
        role_map = {lr.item_id: lr.role_name for lr in roles}
        result = defaultdict(list)
        for project_id, role_name in role_map.items():
            result[str(project_id)].append(role_name)
        return result

    @hybrid_property
    def project_roles(self):
        """Return roles related to this project user profile."""
        return self._project_roles

    @project_roles.setter
    def project_roles(self, roles_map: dict):
        """Update the Projects that this user has customer_user role."""
        from briefy.leica.models import Project
        for project_id, new_roles in roles_map.items():
            project = Project.get(project_id)
            set_local_roles_by_principal(project, self.id, new_roles)

    @property
    def projects(self):
        """Return Projects attached to this profile."""
        from briefy.leica.models import Project
        project_ids = self.project_ids
        return Project.query().filter(Project.id.in_(project_ids)).all()

    def summarize_relations(self, objs):
        """Return a summarized version of an object."""
        response = []
        for obj in objs:
            response.append(
                {
                    'id': obj.id,
                    'title': obj.title,
                    'state': obj.state,
                }
            )
        return response

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['customers'] = self.summarize_relations([self.customer])
        data['projects'] = self.summarize_relations(self.projects)
        return data


class InternalUserProfile(UserProfile):
    """A Briefy user on our system."""

    __tablename__ = 'internaluserprofiles'

    _workflow = workflows.InternalUserProfileWorkflow

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
