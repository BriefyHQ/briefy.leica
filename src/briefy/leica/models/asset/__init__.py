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
from sqlalchemy_utils import JSONType
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


missing_sentinel = object()
def ca_info(info=None, title='', validator=None, typ=None, type_=None, mandatory=False, missing=missing_sentinel):
    """Generate dictionary to be used by colanderalchemy"""

    if not info: info = {}
    info['colanderalchemy'] = {}
    info['colanderalchemy']['title'] = title
    info['colanderalchemy']['typ'] = typ or type_ or colander.String
    if validator: info['colanderalchemy']['validator'] = validator
    if not mandatory or missing != missing_sentinel:
        info['colanderalchemy']['missing'] = missing if missing != missing_sentinel else colander.drop

    return info


class AuthoredMixin:
    owner = sa.Column(sa.String(255), nullable=False)
    """Denormalized string with the name of the OWNER of an asset.

    Owner as in under copyright law, disregarding whether them are a Briefy system user
    """
    ownership_notes = sa.Column(JSONType,
                                default={},
                                info=ca_info(title='Ownership Notes'))
    """To be filled in case ownership "is complicated".

    Can be mostly left blank  - but could be used to anotate works in
    Public Domain, or describing the form of acquisition in cases of
    unknown authorship.

    Kept as JSON, because it might be important to have the owner contact
    information and even physical address in some cases, or things like
    copyright expiration date.

    Until more functionality is required from this field, the suggestion is
    to create a single "notes" key containing non-structured textual information.

    """


class Asset(asset.Asset, mixins.LeicaVersionedMixin, AuthoredMixin, Base):
    """Base class for a deliverable asset from an Assignment.

    All deliverables to Octopus clients are Assets - which are seen by the customer
    as grouped in "orders" and by creative professionals grouped inside
    "assignments".

    From the system point of view an Asset may be a simple Picture, a video file,
    videos or photos encoded in ways to provide imersive expericense such as 360 photos,
    "walktroughs" combining various individual special pictures in a
    specialized 3rd party viewing system, music files, and even text.

    Instances of Asset subclasses contain the relevant information needed for
    updating by professionals, content review, archiving, history keeping, transform,
    delivering and other handling of this content.

    The current system needs, after the order is delivered, of four main "entry points"
    to "see" an asset - which are provided by means of URLs, and visible as properties:
       - source_url: URL to the original asset as input by the professional,
       - archive_url: URL to archival version of asset - must be a version keeping the maximun
                      details that can be achieved given the input files - for example,
                      original image size and a raw file in the case of pictures
                      - original pictures to compose a larger imersive environment
                      if octopus at any time provides an internal solution for that,
                      PSD, XCF, .blend project files and so on. Depending on the
                      destination system pointed by this URL it might be a folder URL
                      (like gdrive), or an archival file containing itself several other files
                      (zip file).
        - preview_url: URL to a static image preview of the asset, whatever its kind.
                       Think "thumbnail" for videos and images.
        - main_delivery_url: Final deliverable form of the asset as acessible by the customer, choosen
                             from "delivery_urls" according to order specifications.
    Besides that, an extended property:
        - delivery_urls: is a list of structured data containing all delivery_urls acessible to the
                        customer along with meta-information such as which version is that
                        regarding size, or availability dates . Needed as often
                        customers will have asset deliveries in different versions (size, file size,
                        video preview,) or different storages (google drive, S3, SFTP). Will
                        often list a single URL which is the same as "-main_delivery_url".


    In order to Spec each kind of asset in order for the system to make sense of how to check for
    its constraints, and present the apropriate interfaces for uploading and downloading, we
    have one class-level field that details the fields that should be available under "metadata" -
    like "width" and "height" for images, "lenght" for video, and so on.

    """

    SPEC = None

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
        info=ca_info(title='Type', missing='image')
    )


    professional_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('professionals.id'),
        index=True,
        info=ca_info(title='ID', validator=colander.uuid, mandatory=True),
        nullable=False
    )
    """Refer to a system user - to be reachable through microservices/redis."""

    uploaded_by = sa.Column(
        sautils.UUIDType,
        info=ca_info(title='Uploaded By', validator=colander.uuid, mandatory=True),
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

    history = sa.Column(JSONType, nullable=True)
    """History.

    An unified list of comments and transitions and modifications.

    Each item can refer to:

      * A  new comment by some user (comments are full objects with workflow)
      * A transition on the object workflow
      * An editing operation on the main asset that results in a new binary,
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
        return self.assignment.order.tech_requirements

    @property
    def check_requirements(self) -> list:
        """Compare metadata with tech requirements.

        :return: A list with validation failures, if any.
        """
        raise ValueError("""Tech requirements validation if done off-process upon transitioning the assignment to QA state""")  # noQA

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

    SPEC = {
        'width': None
    }

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


