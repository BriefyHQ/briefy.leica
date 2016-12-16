"""A Professional for Briefy."""
from briefy.common.db.mixins import PersonalInfoMixin
from briefy.common.db.mixins.optin import OptIn
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.professional.workflows import ProfessionalWorkflow
from briefy.leica.models.professional.workflows import SkillWorkflow
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class ContactInfoMixin:
    """A mixin to manage contact information of a professional."""

    main_email = sa.Column(sautils.types.EmailType(), nullable=True, unique=False)
    main_mobile = sa.Column(sautils.types.PhoneNumberType(), nullable=True, unique=False)


class ProfessionalMixin(ContactInfoMixin, PersonalInfoMixin, OptIn, mixins.KLeicaVersionedMixin):
    """A Professional on our system."""

    pass


class Professional(ProfessionalMixin, Base):
    """A Professional on our system."""

    _workflow = ProfessionalWorkflow

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'profiles', 'links', 'locations', 'type'
        ]
    }

    id = sa.Column(
        UUIDType(binary=False),
        unique=True,
        primary_key=True,
        info={'colanderalchemy': {
              'title': 'Professional id',
              'validator': colander.uuid,
              'missing': colander.drop,
              'typ': colander.String}}
    )

    # Profile information
    photo_path = sa.Column(sa.String(255), nullable=True)

    # Jobs
    jobs = orm.relationship(
        'JobAssignment',
        backref=orm.backref('professional', lazy='joined'),
        lazy='dynamic'
    )

    # Assets
    assets = orm.relationship(
        'Asset',
        backref=orm.backref('professional', lazy='joined'),
        lazy='dynamic'
    )

    # Links
    links = orm.relationship(
        'Link',
        backref='professional',
        cascade='all, delete-orphan',
        lazy='joined'
    )

    # Locations
    locations = orm.relationship(
        'WorkingLocation',
        backref=orm.backref(
            'professional', lazy='joined'
        ),
        cascade='all, delete-orphan',
        lazy='joined'
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


class Skill(mixins.LeicaMixin):
    """A Skill of a professional."""

    _workflow = SkillWorkflow

    @declared_attr
    def id(cls):
        """Id for this skill."""
        return sa.Column(
            UUIDType(binary=False),
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
