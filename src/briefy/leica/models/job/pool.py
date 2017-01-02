"""Briefy Leica Job Pool."""
from briefy.common.db.mixins import Timestamp
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import mixins
from briefy.leica.models.job import workflows
from sqlalchemy import orm

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class ProfessionalsInPool(Timestamp, Base):
    """Relationshiop between Professional and JobPool."""

    __session__ = Session
    __tablename__ = 'professionals_in_pool'

    workflow = None  # this model do not have workflow instance

    pool_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('jobpools.id'),
        primary_key=True,
        info={
            'colanderalchemy': {
                'title': 'Job Pool ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
    )
    """Job Pool ID.

    Foreignkey to :class:`briefy.leica.models.job.pool.JobPool`.
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
        'JobPool',
        back_populates='professionals'
    )
    """Job Pool.

    Relationship with :class:`briefy.leica.models.job.pool.JobPool`.
    """

    professional = orm.relationship(
        'Professional',
        back_populates='pools'
    )
    """Professional.

    Relationship with :class:`briefy.leica.models.professional.Professional`.
    """


class JobPool(mixins.KLeicaVersionedMixin, Base):
    """A Job Pool."""

    _workflow = workflows.JobPoolWorkflow

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

    # Job Assignments
    assignments = orm.relationship(
        'JobAssignment',
        backref=orm.backref('pool')
    )
    """Job Assignments.

    Relationship with :class:`briefy.leica.models.job.JobAssignment`.
    """

    professionals = orm.relationship(
        'ProfessionalsInPool',
        back_populates='pool'
    )
