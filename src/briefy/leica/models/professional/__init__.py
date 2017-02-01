"""A Professional for Briefy."""
from briefy.leica.db import Base
from briefy.leica.models.descriptors import MultipleRelationshipWrapper
from briefy.leica.models.descriptors import UnaryRelationshipWrapper
from briefy.leica.models.professional.workflows import ProfessionalWorkflow
from briefy.leica.models.professional.link import Link
from briefy.leica.models.professional.location import WorkingLocation
from briefy.leica.models.professional.location import MainWorkingLocation
from briefy.leica.models.user import UserProfile
from briefy.leica.utils.user import add_user_info_to_state_history
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa


class Professional(UserProfile, Base):
    """A Professional on our system."""

    __tablename__ = 'professionals'

    __table_args__ = {'extend_existing': True}

    __mapper_args__ = {
        'polymorphic_identity': 'professionals',
    }

    _workflow = ProfessionalWorkflow

    __summary_attributes__ = [
        'id', 'title', 'description', 'created_at', 'updated_at', 'state',
        'email', 'mobile', 'type', 'photo_path', 'slug'
    ]

    __summary_attributes_relations__ = ['links', 'main_location', 'locations', 'pools']

    __listing_attributes__ = __summary_attributes__

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'profiles', 'type', 'external_id'
        ],
        'overrides': {
            'pools_ids': {
              'title': 'pool ids',
              'default': [],
              'missing': colander.drop,
              'typ': colander.List()
            },
            'mobile':  {
                'title': 'Mobile phone number',
                'default': '',
                'missing': colander.drop,
                'typ': colander.String
            },
        }
    }

    __raw_acl__ = (
        ('create', ('g:briefy_scout', 'g:briefy_finance', 'g:briefy_qa', 'g:system')),
        ('list', ('g:briefy', 'g:system')),
        ('view', ('g:briefy', 'g:system')),
        ('edit', ('g:briefy_scout', 'g:briefy_finance', 'g:briefy_pm', 'g:system')),
        ('delete', ('g:briefy_finance', 'g:system')),
    )

    id = sa.Column(
        UUIDType(),
        sa.ForeignKey('userprofiles.id'),
        unique=True,
        primary_key=True,
        info={'colanderalchemy': {
              'title': 'Professional id',
              'validator': colander.uuid,
              'missing': colander.drop,
              'typ': colander.String}}
    )

    accept_travel = sa.Column(sa.Boolean(), default=False, index=True)
    """Accept travel to other locations to work."""

    @declared_attr
    def title(cls):
        """Return the Professional fullname."""
        return orm.column_property(cls.first_name + " " + cls.last_name)

    # Profile information
    photo_path = sa.Column(
        sa.String(255),
        nullable=True,
        info={'colanderalchemy': {
              'title': 'Photo Path',
              'missing': colander.drop,
              'typ': colander.String}}
    )

    # assignments
    assignments = orm.relationship(
        'Assignment',
        lazy='dynamic'
    )

    # Assets
    assets = orm.relationship(
        'Asset',
        backref=orm.backref('professional'),
        lazy='dynamic'
    )

    # Links
    _links = orm.relationship(
        'Link',
        backref='professional',
        cascade='all, delete-orphan',
        info={
            'colanderalchemy': {
                'title': 'Links',
                'missing': colander.drop
            }
        }
    )

    links = MultipleRelationshipWrapper(
        '_links', Link, 'professional_id'
    )
    """Descriptor to handle multiple links get, set and delete."""

    # Locations
    _locations = orm.relationship(
        'WorkingLocation',
        backref=orm.backref(
            'professional',
            enable_typechecks=False,
        ),
        cascade='all, delete-orphan',
        info={
            'colanderalchemy': {
                'title': 'Locations',
                'missing': colander.drop
            }
        }
    )

    locations = MultipleRelationshipWrapper(
        '_locations', WorkingLocation, 'professional_id'
    )
    """Descriptor to handle multiple location get, set and delete."""

    _main_location = orm.relationship(
        'MainWorkingLocation',
        uselist=False,
        viewonly=False,
        cascade='all, delete-orphan',
        info={
            'colanderalchemy': {
                'title': 'Main Location',
                'missing': colander.drop
            }
        }
    )
    """Order Location.

    Relationship with :class:`briefy.leica.models.job.location.OrderLocation`.
    """

    main_location = UnaryRelationshipWrapper(
        '_main_location', MainWorkingLocation, 'professional_id'
    )
    """Descriptor to handle main location get, set and delete."""

    pools = orm.relationship(
        'Pool',
        secondary='professionals_in_pool',
        back_populates='professionals'
    )

    @declared_attr
    def _external_model_(cls):
        """Name of the model on Knack."""
        return 'Photographer'

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['slug'] = self.slug
        data['locations'] = self.locations
        data['links'] = self.links

        # Workflow history
        add_user_info_to_state_history(self.state_history)

        return data


class Photographer(Professional):
    """A Photographer."""

    __tablename__ = 'photographers'

    __table_args__ = {'extend_existing': True}

    __mapper_args__ = {
        'polymorphic_identity': 'photographers',
    }

    id = sa.Column(
        UUIDType(),
        sa.ForeignKey('professionals.id'),
        unique=True,
        primary_key=True,
        info={'colanderalchemy': {
              'title': 'Photographer id',
              'validator': colander.uuid,
              'missing': colander.drop,
              'typ': colander.String}}
    )


class Videographer(Professional):
    """A Videographer."""

    __tablename__ = 'videographers'

    __table_args__ = {'extend_existing': True}

    __mapper_args__ = {
        'polymorphic_identity': 'videographers',
    }

    id = sa.Column(
        UUIDType(),
        sa.ForeignKey('professionals.id'),
        unique=True,
        primary_key=True,
        info={'colanderalchemy': {
              'title': 'Videographer id',
              'validator': colander.uuid,
              'missing': colander.drop,
              'typ': colander.String}}
    )
