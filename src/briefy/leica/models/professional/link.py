"""A link (external resource) of a Briefy Professional."""
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.professional import workflows
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils import URLType
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa


class Link(mixins.LeicaMixin, Base):
    """A Link (external resource) of a Briefy Professional."""

    _workflow = workflows.LinkWorkflow

    professional_id = sa.Column(
        UUIDType(binary=False), sa.ForeignKey('professionals.id'), unique=False,
        info={'colanderalchemy': {
            'title': 'Professional id',
            'validator': colander.uuid,
            'missing': colander.drop,
            'typ': colander.String}}
    )
    type = sa.Column(sa.String(50))
    url = sa.Column(URLType, nullable=False)

    @declared_attr
    def is_social(cls) -> bool:
        """Check if this link points to a social network?."""
        cls_name = cls.__name__.lower()
        default = False if cls_name in ('link', 'porfolio') else True
        return sa.Column(sa.Boolean, default=default)

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

    @declared_attr
    def __tablename__(self):
        """Define tablename.

        For all subtypes we will use the same table.
        """
        return 'links'


class Portfolio(Link):
    """A Portfolio for a Professional."""


class Facebook(Link):
    """A Facebook profile for a Professional."""


class Instagram(Link):
    """A Instagram profile for a Professional."""


class Twitter(Link):
    """A Twitter profile for a Professional."""


class Tumblr(Link):
    """A Tumblr profile for a Professional."""


class Flickr(Link):
    """A Flickr profile for a Professional."""


class Youtube(Link):
    """A Youtube profile for a Professional."""
