"""A Professional for Briefy."""
from briefy.common.db.mixins import PersonalInfoMixin
from briefy.common.db.mixins.optin import OptIn
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.professional.workflows import ProfessionalWorkflow
from briefy.ws.utils.user import add_user_info_to_state_history
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class ContactInfoMixin:
    """A mixin to manage contact information of a professional."""

    main_email = sa.Column(
        sautils.types.EmailType(),
        nullable=True,
        unique=False,
        info={
            'colanderalchemy': {
                'title': 'Email',
                'default': '',
                'typ': colander.String
            }
        }
    )

    main_mobile = sa.Column(
        sautils.types.PhoneNumberType(),
        nullable=True,
        unique=False,
        info={
            'colanderalchemy': {
                'title': 'Mobile phone number',
                'default': '',
                'typ': colander.String
            }
        }
    )


class ProfessionalMixin(ContactInfoMixin, PersonalInfoMixin, OptIn, mixins.KLeicaVersionedMixin):
    """A Professional on our system."""

    pass


class Professional(ProfessionalMixin, Base):
    """A Professional on our system."""

    _workflow = ProfessionalWorkflow

    __summary_attributes__ = [
        'id', 'title', 'description', 'created_at', 'updated_at', 'state',
        'main_email', 'main_mobile', 'type', 'photo_path', 'slug'
    ]

    __summary_attributes_relations__ = ['links', 'main_location', 'locations', 'pools']

    __listing_attributes__ = __summary_attributes__

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'profiles', 'links', 'locations', 'type', 'main_location'
        ]
    }

    id = sa.Column(
        UUIDType(),
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

    @synonym_for("main_email")
    @property
    def email(self):
        """Return the Professional email."""
        return self.main_email

    @synonym_for("main_mobile")
    @property
    def mobile(self):
        """Return the Professional mobile phone."""
        return self.main_mobile

    # Profile information
    photo_path = sa.Column(sa.String(255), nullable=True)

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
    links = orm.relationship(
        'Link',
        backref='professional',
        cascade='all, delete-orphan',
    )

    # Locations
    locations = orm.relationship(
        'WorkingLocation',
        backref=orm.backref(
            'professional'
        ),
        cascade='all, delete-orphan',
    )

    main_location = orm.relationship(
        'MainWorkingLocation',
        uselist=False,
        viewonly=False,
        cascade='all, delete-orphan',
    )

    pools = orm.relationship(
        'Pool',
        secondary='professionals_in_pool',
        back_populates='professionals'
    )

    type = sa.Column(sa.String(50), nullable=False)

    @hybrid_property
    def user_id(self):
        """User id."""
        return self.id

    @declared_attr
    def _external_model_(cls):
        """Name of the model on Knack."""
        return 'Photographer'

    @declared_attr
    def __mapper_args__(cls):
        """Return polymorphic identity."""
        cls_name = cls.__name__.lower()
        args = {
            'polymorphic_identity': cls_name,
        }
        if cls_name == 'professional':
            args['polymorphic_on'] = cls.type
        return args

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['slug'] = self.slug
        data['locations'] = self.locations

        # Workflow history
        add_user_info_to_state_history(self.state_history)

        return data


class Skill(mixins.LeicaMixin):
    """A Skill of a professional."""

    _workflow = ProfessionalWorkflow

    @declared_attr
    def id(cls):
        """Id for this skill."""
        return sa.Column(
            UUIDType(),
            sa.ForeignKey('professionals.id'),
            primary_key=True,
            info={'colanderalchemy': {
                'title': 'Professional id',
                'validator': colander.uuid,
                'missing': colander.drop,
                'typ': colander.String}}
        )


class Photographer(Skill, Professional):
    """A Photographer."""

    @declared_attr
    def __tablename__(self):
        """Define tablename."""
        return 'photographers'


class Videographer(Skill, Professional):
    """A Videographer."""

    @declared_attr
    def __tablename__(self):
        """Define tablename."""
        return 'videographers'
