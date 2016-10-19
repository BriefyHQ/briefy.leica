"""Briefy Leica Asset model."""
from briefy.common.db.mixins import Image
from briefy.common.db.mixins import Mixin
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows
from briefy.leica.utils import imaging
from briefy.ws.utils.user import add_user_info_to_state_history
from briefy.ws.utils.user import get_public_user_info
from sqlalchemy_continuum.utils import count_versions

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


__summary_attributes__ = [
    'id', 'title', 'filename', 'created_at', 'updated_at', 'state', 'uploaded_by',
    'author_id', 'size', 'width', 'height', 'is_valid', 'image'
]

__listing_attributes__ = [
    'id', 'title', 'filename', 'created_at', 'updated_at', 'state', 'uploaded_by',
    'author_id', 'size', 'width', 'height', 'is_valid', 'image', 'version', 'history'
]


class Asset(Image, Mixin, Base):
    """A deliverable asset from a Job."""

    _workflow = workflows.AssetWorkflow
    __tablename__ = 'assets'

    __versioned__ = {
        'exclude': ['state_history', '_state_history', ]
    }
    __session__ = Session

    __summary_attributes__ = __summary_attributes__
    __listing_attributes__ = __listing_attributes__

    __raw_acl__ = (
        ('list', ('g:briefy_qa', 'g:briefy_pm', 'g:system')),
        ('view', ()),
        ('edit', ()),
        ('delete', ()),
    )

    __actors__ = (
        'author_id',
        'uploaded_by'
    )

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
                                   order_by='asc(Comment.created_at)',
                                   primaryjoin='Comment.entity_id == Asset.id')

    internal_comments = sa.orm.relationship('InternalComment',
                                            foreign_keys='InternalComment.entity_id',
                                            primaryjoin='InternalComment.entity_id == Asset.id')

    @property
    def tech_requirements(self) -> dict:
        """Tech requirements for this asset.

        :return: A dictionary with technical requirements for an asset.
        """
        job = self.job
        return job.tech_requirements

    @property
    def _check_requirements(self) -> list:
        """Compare metadata with tech requirements.

        :return: A list with validation failures, if any.
        """
        response = []
        metadata = self.metadata_
        tech_requirements = self.tech_requirements
        if tech_requirements:
            response = imaging.check_image_constraints(metadata, tech_requirements)
        return response

    @property
    def check_requirements(self) -> list:
        """Compare metadata with tech requirements.

        :return: A list with error messages, if any.
        """
        response = [
            c['text'] for c in self._check_requirements
        ]
        return response

    @property
    def invalid_checks(self) -> list:
        """Return a list of invalid metadata checks.

        :return: A list with invalid metadata, if any.
        """
        response = [
            c['check'] for c in self._check_requirements
        ]
        return response

    @property
    def is_valid(self) -> bool:
        """Compare metadata with tech requirements

        :return: A boolean indicating if this image is valid or not.
        """
        return not self.check_requirements

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

    @property
    def qa_manager(self) -> str:
        """Return the qa_manager id for this object.

        :return: ID of the qa_manager.
        """
        return self.job.qa_manager

    def _apply_actors_info(self, data: dict) -> dict:
        """Apply actors information for a given data dictionary.

        :param data: Data dictionary.
        :return: Data dictionary.
        """
        actors = [(k, k) for k in self.__actors__]
        info = self._actors_info()
        for key, attr in actors:
            value = info.get(attr, None)
            data[key] = get_public_user_info(value) if value else None
        return data

    def to_listing_dict(self) -> dict:
        """Return a summarized version of the dict representation of this Class.

        Used to serialize this object within a parent object serialization.
        :returns: Dictionary with fields and values used by this Class
        """
        data = super().to_listing_dict()
        # data = self._apply_actors_info(data)
        data['metadata'] = self.metadata_
        return data

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict(excludes=['raw_metadata'])
        data['image'] = self.image
        data['metadata'] = self.metadata_
        add_user_info_to_state_history(self.state_history)
        data['author_id'] = get_public_user_info(self.author_id)
        data['uploaded_by'] = get_public_user_info(self.uploaded_by)
        data['is_valid'] = self.is_valid
        data['invalid_checks'] = self.invalid_checks
        return data
