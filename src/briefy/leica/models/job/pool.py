"""Briefy Leica Pool."""
from briefy.common.db.mixins import Timestamp
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import Assignment
from briefy.leica.models import mixins
from briefy.leica.models.job import workflows
from briefy.leica.models.professional import Professional
from sqlalchemy import func
from sqlalchemy import orm
from sqlalchemy import select
from sqlalchemy.sql import and_, not_
from sqlalchemy.ext.declarative import declared_attr

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
        'country',
    ]
    __listing_attributes__ = __summary_attributes__ + [
        'total_assignments', 'total_professionals', 'live_assignments'
    ]

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

    @declared_attr
    def total_assignments(cls) -> int:
        """Return the total number of Assignments in the Pool."""
        stmt = select([func.count(Assignment.id)]).where(
            Assignment.pool_id == cls.id
        ).as_scalar()
        return orm.column_property(stmt)

    @declared_attr
    def live_assignments(cls) -> int:
        """Return the number of 'active' Assignments in the Pool."""
        end_states = ('cancelled', 'approved', 'completed', 'perm_rejected')
        stmt = select([func.count(Assignment.id)]).where(
            and_(
                Assignment.pool_id == cls.id,
                not_(Assignment.state.in_(end_states))
            )
        ).as_scalar()
        return orm.column_property(stmt)

    @declared_attr
    def total_professionals(cls) -> int:
        """Return the total number of Professionals in the Pool."""
        stmt = select([func.count(Professional.id)]).where(
            and_(
                ProfessionalsInPool.professional_id == Professional.id,
                ProfessionalsInPool.pool_id == cls.id
            )
        ).as_scalar()
        return orm.column_property(stmt)

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['slug'] = self.slug
        return data
