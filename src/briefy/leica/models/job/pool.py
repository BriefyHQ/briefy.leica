"""Briefy Leica Pool."""
from briefy.common.db.mixins import Timestamp
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import mixins
from briefy.leica.models.job import workflows
from sqlalchemy import orm

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class ProfessionalsInPool(mixins.VersionMixin, Timestamp, Base):
    """Relationshiop between Professional and Pool."""

    __session__ = Session
    __tablename__ = 'professionals_in_pool'

    workflow = None  # this model do not have workflow instance

    pool_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('pools.id'),
        primary_key=True,
        info={
            'colanderalchemy': {
                'title': 'Pool ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
    )
    """Pool ID.

    Foreignkey to :class:`briefy.leica.models.job.pool.Pool`.
    """

    professional_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('professionals.id'),
        primary_key=True,
        info={
            'colanderalchemy': {
                'title': 'Professional ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
    )
    """Professional ID.

    Foreignkey to :class:`briefy.leica.models.professional.Professional`.
    """

    pool = orm.relationship(
        'Pool'
    )
    """Pool.

    Relationship with :class:`briefy.leica.models.job.pool.Pool`.
    """

    professional = orm.relationship(
        'Professional'
    )
    """Professional.

    Relationship with :class:`briefy.leica.models.professional.Professional`.
    """


class Pool(mixins.KLeicaVersionedMixin, Base):
    """A Pool."""

    _workflow = workflows.PoolWorkflow

    __summary_attributes__ = [
        'id', 'title', 'description', 'slug', 'created_at', 'updated_at', 'state',
    ]
    __listing_attributes__ = __summary_attributes__

    __colanderalchemy_config__ = {'excludes': [
        'state_history', 'state'
    ]}

    __raw_acl__ = (
        ('list', ('g:briefy_qa', 'g:briefy_bizdev', 'g:briefy_pm', 'g:system')),
        ('view', ()),
        ('edit', ()),
        ('delete', ()),
    )

    country = sa.Column(sautils.CountryType, nullable=False)
    """Country of this Pool.

    Country will be stored as a ISO 3166-2 information.
    i.e.: DE, BR, ID
    """

    # Assignments
    assignments = orm.relationship(
        'Assignment',
        backref=orm.backref('pool')
    )
    """Assignments.

    Relationship with :class:`briefy.leica.models.job.Assignment`.
    """

    professionals = orm.relationship(
        'Professional',
        secondary='professionals_in_pool',
        back_populates='pools'
    )

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['slug'] = self.slug
        return data
