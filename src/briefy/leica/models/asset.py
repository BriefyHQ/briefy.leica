"""Briefy Leica Asset model."""
from briefy.common.db.mixins import Image
from briefy.common.db.mixins import Mixin
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows


import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class Asset(Image, Mixin, Base):
    """A deliverable asset from a Job."""

    _workflow = workflows.AssetWorkflow
    __tablename__ = 'assets'
    __session__ = Session

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', 'history',
                                               'raw_metadata',
                                               'comments', 'internal_comments', 'job']}

    title = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, default='')
    version = sa.Column(sa.Integer, nullable=False, default=0)

    # Denormalized string with the name of the OWNER of
    # an asset under copyright law, disregarding whether he is a Briefy systems uer
    owner = sa.Column(sa.String(255), nullable=False)
    # Refers to a system user - reachable through microservices/redis
    author_id = sa.Column(sautils.UUIDType,
                          info={'colanderalchemy': {
                              'title': 'ID',
                              'validator': colander.uuid,
                              'typ': colander.String}},
                          nullable=False)

    job_id = sa.Column(sautils.UUIDType,
                       sa.ForeignKey('jobs.id'),
                       nullable=False,
                       info={'colanderalchemy': {
                           'title': 'ID',
                           'validator': colander.uuid,
                           'typ': colander.String}}
                       )
    job = sa.orm.relationship('Job', uselist=False, back_populates='assets')

    # history is an unified list where each entry can refer to:
    # - A  new comment by some user (comments are full objects with workflow)
    # - A transition on the object workflow
    # - An editing operation on the mains asset that results in a new binary -
    #        this can be the result of:
    #        -  a new upload that superseeds an earlier version,
    #        - an internal operation (crop, filter, so on)
    #        -
    history = sa.Column(sautils.JSONType, nullable=True)

    comments = sa.orm.relationship('Comment',
                                   foreign_keys='Comment.entity_id',
                                   primaryjoin='Comment.entity_id == Asset.id')

    internal_comments = sa.orm.relationship('InternalComment',
                                            foreign_keys='InternalComment.entity_id',
                                            primaryjoin='InternalComment.entity_id == Asset.id')

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['image'] = self.image
        data['metadata'] = self.metadata_
        return data
