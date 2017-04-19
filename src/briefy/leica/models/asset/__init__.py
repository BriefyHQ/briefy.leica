"""Briefy Leica Asset model."""
from briefy.common.db.mixins import asset
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.asset import workflows
from briefy.leica.models.mixins import get_public_user_info
from briefy.leica.utils import imaging
from briefy.leica.utils.user import add_user_info_to_state_history
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


__summary_attributes__ = [
    'id', 'title', 'filename', 'created_at', 'updated_at', 'state', 'uploaded_by',
    'professional_id', 'size', 'width', 'height', 'is_valid', 'image'
]

__listing_attributes__ = [
    'id', 'title', 'filename', 'created_at', 'updated_at', 'state', 'uploaded_by',
    'professional_id', 'size', 'width', 'height', 'is_valid', 'image', 'version', 'history'
]


class Asset(asset.Asset, mixins.LeicaVersionedMixin, Base):
    """A deliverable asset from an Assignment."""

    _workflow = workflows.AssetWorkflow

    __summary_attributes__ = __summary_attributes__
    __listing_attributes__ = __listing_attributes__

    __raw_acl__ = (
        ('list', ('g:briefy', 'g:system')),
        ('create', ('g:briefy_qa', 'g:system')),
        ('view', ('g:briefy', 'g:system')),
        ('edit', ('g:briefy_qa', 'g:system')),
        ('delete', ('g:briefy_qa', 'g:system')),
    )

    __actors__ = (
        'professional_id',
        'uploaded_by'
    )

    __colanderalchemy_config__ = {'excludes': [
        'state_history', 'state', 'history', 'raw_metadata', 'professional',
        'comments', 'assignment'
    ]}

    type = sa.Column(
        sa.String(50), nullable=False,
        info={'colanderalchemy': {
            'title': 'Type',
            'missing': 'image',
            'typ': colander.String}
        },
    )

    owner = sa.Column(sa.String(255), nullable=False)
    """Denormalized string with the name of the OWNER of an asset.

    Owner as in under copyright law, disregarding whether them are a Briefy system user
    """

    professional_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('professionals.id'),
        index=True,
        info={
            'colanderalchemy': {
                'title': 'ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        },
        nullable=False
    )
    """Refer to a system user - reachable through microservices/redis."""

    uploaded_by = sa.Column(
        sautils.UUIDType,
        info={
            'colanderalchemy': {
                'title': 'Uploaded by',
                'validator': colander.uuid,
                'typ': colander.String
            }
        },
        nullable=False
    )
    """Refer to a system user - reachable through microservices/redis.

    Sometimes an internal briefy staff - other than the assigned professional
    needs to update an asset. This records the one who actually uploaded the item.
    """

    assignment_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('assignments.id'),
        index=True,
        nullable=False,
        info={
            'colanderalchemy': {
                'title': 'External ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
    )
    """Assignment ID.

    Assignment shooting under which this asset has been generated.
    """

    history = sa.Column(sautils.JSONType, nullable=True)
    """History.

    An unified list of comments and transitions and modifications.

    Each item can refer to:

      * A  new comment by some user (comments are full objects with workflow)
      * A transition on the object workflow
      * An editing operation on the mains asset that results in a new binary,
        this can be the result of:
        * a new upload that superseeds an earlier version,
        * an internal operation (crop, filter, so on)

    """

    comments = orm.relationship(
        'Comment',
        foreign_keys='Comment.entity_id',
        order_by='asc(Comment.created_at)',
        primaryjoin='Comment.entity_id == Asset.id'
    )
    """Comments."""

    @property
    def tech_requirements(self) -> dict:
        """Technical requirements for this asset.

        :return: A dictionary with technical requirements for an asset.
        """
        assignment = self.assignment
        return assignment.order.tech_requirements

    @property
    def check_requirements(self) -> list:
        """Compare metadata with tech requirements.

        :return: A list with validation failures, if any.
        """
        return True

    @property
    def is_valid(self) -> bool:
        """Compare metadata with tech requirements.

        :return: A boolean indicating if this image is valid or not.
        """
        return not self.check_requirements

    @property
    def qa_manager(self) -> str:
        """Return the qa_manager id for this object.

        :return: ID of the qa_manager.
        """
        return self.assignment.qa_manager

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
        data['professional'] = get_public_user_info(self.professional_id)
        data['uploaded_by'] = get_public_user_info(self.uploaded_by)
        data['is_valid'] = self.is_valid
        data['invalid_checks'] = [
            c['check'] for c in self.check_requirements
        ]
        return data

    @declared_attr
    def __mapper_args__(cls):
        """Return polymorphic identity."""
        cls_name = cls.__name__.lower()
        args = {
            'polymorphic_identity': cls_name,
        }
        if cls_name == 'asset':
            args['polymorphic_on'] = cls.type
        return args


class Image(asset.ImageMixin, Asset):
    """A deliverable Image from an Assignment."""

    __tablename__ = 'images'

    @declared_attr
    def id(cls):
        """Id for this Image."""
        return sa.Column(
            UUIDType(),
            sa.ForeignKey('assets.id'),
            index=True,
            primary_key=True,
            info={'colanderalchemy': {
                'title': 'Asset id',
                'validator': colander.uuid,
                'missing': colander.drop,
                'typ': colander.String}}
        )

    @property
    def check_requirements(self) -> list:
        """Compare metadata with tech requirements.

        :return: A list with validation failures, if any.
        """
        response = []
        metadata = self.metadata_
        tech_requirements = self.tech_requirements
        asset_requirements = tech_requirements.get('asset') if tech_requirements else {}
        if asset_requirements:
            response = imaging.check_image_constraints(metadata, asset_requirements)
        return response


class ThreeSixtyImage(asset.ThreeSixtyImageMixin, Asset):
    """A deliverable 360Image from an Assignment."""

    __tablename__ = 'threesixtyimages'

    @declared_attr
    def id(cls):
        """Id for this Image."""
        return sa.Column(
            UUIDType(),
            sa.ForeignKey('assets.id'),
            index=True,
            primary_key=True,
            info={'colanderalchemy': {
                'title': 'Asset id',
                'validator': colander.uuid,
                'missing': colander.drop,
                'typ': colander.String}}
        )

    @property
    def check_requirements(self) -> list:
        """Compare metadata with tech requirements.

        :return: A list with validation failures, if any.
        """
        # TODO: Check requirements
        return True


class Video(asset.VideoMixin, Asset):
    """A deliverable Video from an Assignment."""

    __tablename__ = 'videos'

    @declared_attr
    def id(cls):
        """Id for this Image."""
        return sa.Column(
            UUIDType(),
            sa.ForeignKey('assets.id'),
            index=True,
            primary_key=True,
            info={'colanderalchemy': {
                'title': 'Asset id',
                'validator': colander.uuid,
                'missing': colander.drop,
                'typ': colander.String}}
        )

    @property
    def check_requirements(self) -> list:
        """Compare metadata with tech requirements.

        :return: A list with validation failures, if any.
        """
        # TODO: Check requirements
        return True
