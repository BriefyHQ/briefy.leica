"""A link (external resource) of a Briefy Professional."""
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.professional import workflows
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import URLType
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa


class Link(mixins.LeicaMixin, Base):
    """A Link (external resource) of a Briefy Professional."""

    _workflow = workflows.LinkWorkflow

    __colanderalchemy_config__ = {
        'excludes': ['state_history', 'state']
    }

    professional_id = sa.Column(
        UUIDType(), sa.ForeignKey('professionals.id'), unique=False,
        info={'colanderalchemy': {
            'title': 'Professional id',
            'validator': colander.uuid,
            'missing': colander.drop,
            'typ': colander.String}}
    )
    type = sa.Column(sa.String(50))
    url = sa.Column(URLType, nullable=False)

    @hybrid_property
    def is_social(self) -> bool:
        """Check if this link points to a social network?."""
        return False if self.type in ('link', 'portfolio') else True

    @is_social.expression
    def is_social(cls):
        """Check if this link points to a social network?."""
        return sa.not_(cls.type.in_(('link', 'porfolio', )))

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


class FiveHundred(Link):
    """A 500px profile for a Professional."""


class Youtube(Link):
    """A Youtube profile for a Professional."""


class GDrive(Link):
    """A Google Drive profile for a Professional."""


class Linkedin(Link):
    """A Linkedin profile for a Professional."""
