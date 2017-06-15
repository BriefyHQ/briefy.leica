"""User profile information."""
from briefy.common.db.models import Item
from briefy.common.db.models.local_role import LocalRole
from briefy.common.utils import schema
from briefy.leica import logger
from briefy.leica.models import Customer
from briefy.leica.models import mixins
from briefy.leica.models.user import workflows
from briefy.leica.utils import ensure_uid
from briefy.leica.utils.user import add_user_info_to_state_history
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.session import object_session
from sqlalchemy_utils import UUIDType
from uuid import UUID

import colander
import copy
import sqlalchemy as sa


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
        'email', 'mobile', 'type', 'slug'
    ]

    __summary_attributes_relations__ = []

    __listing_attributes__ = __summary_attributes__ + ['internal', 'company_name']

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'type', 'external_id', '_owner', '_customer_roles',
            '_project_roles'

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

    @declared_attr
    def title(cls):
        """Return the User fullname."""
        return sa.orm.column_property(cls.first_name + ' ' + cls.last_name)

    def to_dict(self, excludes: list=None, includes: list=None):
        """Return a dict representation of this object."""
        data = super().to_dict(excludes=excludes, includes=includes)
        add_user_info_to_state_history(self.state_history)
        return data


class CustomerUserProfile(UserProfile):
    """A Customer on our system."""

    __tablename__ = 'customeruserprofiles'

    _workflow = workflows.CustomerUserProfileWorkflow

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

    customer_id = sa.Column(
        UUIDType(),
        sa.ForeignKey('customers.id'),
        index=True,
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
            foreign_keys='LocalRole.principal_id',
            viewonly=True,
            primaryjoin="""and_(
                        LocalRole.principal_id==CustomerUserProfile.id,
                        LocalRole.item_id==CustomerUserProfile.customer_id,
                        LocalRole.role_name=="customer_user"
                    )"""
        )

    @hybrid_property
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
            foreign_keys='LocalRole.principal_id',
            viewonly=True,
            uselist=True,
            primaryjoin="""and_(
                        LocalRole.principal_id == CustomerUserProfile.id,
                        LocalRole.item_id==CustomerUserProfile.customer_id,
                        LocalRole.role_name=="customer_user"
                    )"""
        )

    @property
    def customers(self):
        """Return Customers attached to this profile."""
        customer_ids = self.customer_ids
        return Customer.query().filter(Customer.id.in_(customer_ids)).all()

    @hybrid_property
    def project_roles(self):
        """Return roles related to this project user profile."""
        return self._project_roles

    @project_roles.setter
    def project_roles(self, project_ids):
        """Update the Projects that this user has customer_user role."""
        project_ids = set(project_ids)
        current_projects = {role.entity_id for role in self._project_roles}
        to_add = project_ids - current_projects
        to_remove = current_projects - project_ids

        def validate_project(project_id):
            """Get project instance and validate."""
            from briefy.leica.models import Project
            project = Project.get(project_id)
            if not project:
                raise ValueError('There is not Project with ID: {0}'.format(project_id))

            if project.customer_id not in self.customer_ids:
                msg = 'Project "{0}" is not linked ot the Customer the user belongs.'
                # TODO: this can not be validated here, it must be before commit the transaction
                logger.warn(msg.format(project.title))
            return project

        def remove_project(project, user_id):
            """Remove customer_user LocalRole from the Project."""
            session = object_session(project)
            local_role = session.query(LocalRole).filter_by(
                entity_id=project.id,
                user_id=user_id,
                role_name='customer_user'
            ).first()
            session.delete(local_role)

        for project_id in to_add:
            project = validate_project(project_id)
            project.customer_users.append(ensure_uid(self.id))

        for project_id in to_remove:
            project = validate_project(project_id)
            remove_project(project, ensure_uid(self.id))

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
        data['customers'] = self.summarize_relations(self.customers)
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
