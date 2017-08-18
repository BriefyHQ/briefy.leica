"""User profile information."""
from briefy.common.db.mixins.local_roles import add_local_role
from briefy.common.db.mixins.local_roles import del_local_role
from briefy.common.db.mixins.local_roles import set_local_roles_by_principal
from briefy.common.db.models import Item
from briefy.common.db.models.local_role import LocalRole
from briefy.common.utils import schema
from briefy.leica.models import Customer
from briefy.leica.models import mixins
from briefy.leica.models.user import workflows
from briefy.leica.utils.user import add_user_info_to_state_history
from copy import deepcopy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class UserProfile(mixins.UserProfileMixin, mixins.UserProfileRolesMixin, Item):
    """A Professional on our system."""

    __tablename__ = 'userprofiles'

    _workflow = workflows.UserProfileWorkflow

    __summary_attributes__ = [
        'id', 'title', 'description', 'created_at', 'updated_at', 'state',
        'email', 'mobile', 'slug', 'fullname'
    ]

    __summary_attributes_relations__ = []

    __listing_attributes__ = __summary_attributes__ + ['internal', 'company_name']

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
        # HACK: initial_password attribute is never persisted, so we need to explicitly add it
        # here when it is set by rolleiflex integration
        # ref: briefy.leica.utils.rolleiflex.create_user
        if hasattr(self, 'initial_password'):
            data['initial_password'] = self.initial_password
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

    __to_dict_additional_attributes__ = [
        'project_customer_pm', 'project_customer_qa', 'customer_roles'
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
                    'typ': colander.List()
                },
                'project_customer_pm': {
                    'title': 'Projects with PM role',
                    'missing': colander.drop,
                    'typ': colander.List()
                },
                'project_customer_qa': {
                    'title': 'Projects with QA role',
                    'missing': colander.drop,
                    'typ': colander.List()
                },
                'owner': {
                    'title': 'Owner IDs',
                    'missing': colander.drop,
                    'typ': colander.List()
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
        pop_attrs = ['project_customer_qa', 'project_customer_pm', 'customer_roles']
        update_kwargs = {}
        for attr in pop_attrs:
            value = payload.pop(attr, None)
            if value:
                update_kwargs[attr] = value
        obj = super().create(payload)
        obj.update(update_kwargs)
        return obj

    @hybrid_property
    def customer(self):
        """Customer object this user belongs."""
        return Customer.get(self.customer_id)

    @property
    def _customer_roles(self) -> list:
        """Get customer roles for this user in the customer context."""
        customer = Customer.get(self.customer_id)
        return [r.role_name for r in customer.local_roles
                if str(r.principal_id) == str(self.id)]

    @hybrid_property
    def customer_roles(self) -> list:
        """Return roles related to this customer user profile."""
        return self._customer_roles

    @customer_roles.setter
    def customer_roles(self, roles: list):
        """Add customer_user role for this customer user profile."""
        customer = self.customer
        set_local_roles_by_principal(customer, self.id, roles)

    @hybrid_property
    def project_ids(self):
        """Return a list of project ids related to the customer the user belongs."""
        roles = LocalRole.query().filter(
            LocalRole.item_type == 'project',
            LocalRole.principal_id == self.id
        )
        return [lr.item_id for lr in roles]

    @hybrid_property
    def _project_roles(self):
        """Local roles of this user in the Customer context as project_user."""
        roles = LocalRole.query().filter(
            LocalRole.item_type == 'project',
            LocalRole.principal_id == self.id
        )
        role_map = {lr.item_id: lr.role_name for lr in roles}
        result = {}
        for project_id, role_name in role_map.items():
            if not result.get(str(project_id)):
                result[str(project_id)] = [role_name]
            else:
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

    def _project_ids_by_role(self, role_name: str) -> list:
        """Return the list of projects ids the user has a local role."""
        roles = LocalRole.query().filter(
            LocalRole.item_type == 'project',
            LocalRole.principal_id == self.id,
            LocalRole.role_name == role_name
        )
        return [str(lr.item_id) for lr in roles]

    def _update_projects_by_role(self, role_name: str, new_project_ids: list) -> list:
        """Update the list of projects the user has a local role."""
        projects = self.customer.projects
        current_project_ids = self._project_ids_by_role(role_name)
        for project in projects:
            project_id = str(project.id)
            session = project.__session__
            if project_id in new_project_ids and project_id not in current_project_ids:
                add_local_role(session, project, role_name, self.id)
            elif project_id not in new_project_ids and project_id in current_project_ids:
                for lr in project.local_roles:
                    if lr.role_name == role_name and lr.principal_id == self.id:
                        del_local_role(session, project, lr)

    @hybrid_property
    def project_customer_pm(self) -> list:
        """Return the list of projects ids the user has project_customer_pm local role."""
        return self._project_ids_by_role('project_customer_pm')

    @project_customer_pm.setter
    def project_customer_pm(self, new_project_ids: list):
        """Update the list of projects that this user has project_customer_pm role."""
        self._update_projects_by_role('project_customer_pm', new_project_ids)

    @hybrid_property
    def project_customer_qa(self) -> list:
        """Return the list of projects ids the user has project_customer_qa local role."""
        return self._project_ids_by_role('project_customer_qa')

    @project_customer_qa.setter
    def project_customer_qa(self, new_project_ids: list):
        """Update the list of projects that this user has project_customer_qa role."""
        self._update_projects_by_role('project_customer_qa', new_project_ids)

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

    def to_dict(self, excludes: list=None, includes: list=None):
        """Return a dict representation of this object."""
        data = super().to_dict(excludes=excludes, includes=includes)
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
