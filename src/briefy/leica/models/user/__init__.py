"""User profile information."""
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.user import workflows
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa


class UserProfile(mixins.UserProfileMixin, Base):
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
            'state_history', 'state', 'type', 'external_id'
        ]
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
        if cls_name == 'link':
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
