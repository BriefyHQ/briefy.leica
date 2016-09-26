"""Briefy Leica Asset model."""
from briefy.common.db.mixins import Image
from briefy.common.db.mixins import Mixin
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows
from sqlalchemy_continuum.utils import count_versions

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class Asset(Image, Mixin, Base):
    """A deliverable asset from a Job."""

    _workflow = workflows.AssetWorkflow
    __tablename__ = 'assets'

    __versioned__ = {
        'exclude': ['state_history', '_state_history', ]
    }
    __session__ = Session

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', 'history',
                                               'raw_metadata',
                                               'comments', 'internal_comments', 'job']}

    title = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, default='')

    # Denormalized string with the name of the OWNER of
    # an asset under copyright law, disregarding whether he is a Briefy systems user
    owner = sa.Column(sa.String(255), nullable=False)
    # Refers to a system user - reachable through microservices/redis
    author_id = sa.Column(sautils.UUIDType,
                          info={'colanderalchemy': {
                              'title': 'ID',
                              'validator': colander.uuid,
                              'typ': colander.String}},
                          nullable=False)

    # Refers to a system user - reachable through microservices/redis
    # This field exists because a QA could be the one that uploaded the image,
    # So this field needs to express that
    uploaded_by = sa.Column(sautils.UUIDType,
                            info={'colanderalchemy': {
                                'title': 'Uploaded by',
                                'validator': colander.uuid,
                                'typ': colander.String}},
                            nullable=False)

    job_id = sa.Column(sautils.UUIDType,
                       sa.ForeignKey('jobs.id'),
                       nullable=False,
                       info={'colanderalchemy': {
                           'title': 'External ID',
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

    @property
    def version(self) -> int:
        """Return the current version number.

        We are civilised here, so version numbering starts from zero ;-)
        :return: Version number of this object.
        """
        versions = count_versions(self)
        return versions - 1

    @version.setter
    def version(self, value: int) -> int:
        """Explicitly sets a version to the asset. (Deprecated)

        XXX: Here only to avoid issues if any client tries to set this.
        :param value:
        """
        pass

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict(excludes=['raw_metadata'])
        data['image'] = self.image
        data['metadata'] = self.metadata_
        return data
