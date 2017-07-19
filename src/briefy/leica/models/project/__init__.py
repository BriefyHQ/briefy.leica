"""Briefy Leica Project model."""
from briefy.common.db.mixins import BriefyRoles
from briefy.common.utils import schema
from briefy.common.utils.data import Objectify
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.common.vocabularies.roles import Groups
from briefy.leica.cache import cache_region
from briefy.leica.cache import enable_cache
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.project import workflows
from briefy.leica.utils.user import add_user_info_to_state_history
from briefy.leica.vocabularies import AssetTypes
from briefy.leica.vocabularies import OrderTypeChoices
from briefy.ws.errors import ValidationError
from sqlalchemy import event
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import JSONB
from zope.interface import implementer
from zope.interface import Interface

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils
import typing as t


# TODO: improve this based on the project type
DEFAULT_DELIVERY_CONFIG = {
    'approve': {
        'archive': {
            'driver': 'gdrive',
            'images': True,
            'name': 'order.customer_order_id',
            'other': True,
            'parentId': None,
            'resize': [],
            'subfolders': True
        },
        'delivery': {
            'driver': 'gdrive',
            'images': True,
            'name': 'order.customer_order_id',
            'other': False,
            'parentId': None,
            'resize': [],
            'subfolders': False
        }
    }
}

DEFAULT_ADD_ORDER_ROLES = [
    'g:customers',
    'g:briefy_pm',
]


class IProject(Interface):
    """Marker interface for Project."""


class CommercialInfoMixin(mixins.ProfessionalPayoutInfo, mixins.ProjectBriefyRoles,
                          mixins.OrderFinancialInfo):
    """Commercial details about a project."""

    contract = sa.Column(
        sautils.URLType,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Contract',
                'validator': colander.url,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Path to contract."""


@implementer(IProject)
class Project(CommercialInfoMixin, BriefyRoles, mixins.KLeicaVersionedMixin, Base):
    """A Project in Briefy."""

    _workflow = workflows.ProjectWorkflow

    __summary_attributes__ = [
        'id', 'title', 'description', 'created_at', 'updated_at', 'state', 'slug', 'asset_types'
    ]

    __summary_attributes_relations__ = ['customer', 'pool']

    __listing_attributes__ = [
        'id', 'title', 'description', 'created_at', 'updated_at', 'state',
        'external_id', 'total_orders', 'slug', 'customer', 'asset_types'
    ]

    __raw_acl__ = (
        ('create', ('g:briefy_pm', 'g:briefy_bizdev', 'g:briefy_finance', 'g:system')),
        ('list', ('g:briefy_qa', 'g:briefy_bizdev',
                  'g:briefy_scout', 'g:briefy_finance', 'g:system')),
        ('view', ('g:briefy_qa', 'g:briefy_bizdev',
                  'g:briefy_scout', 'g:briefy_finance', 'g:system')),
        ('edit', ('g:briefy_pm', 'g:briefy_bizdev', 'g:briefy_finance', 'g:system')),
        ('delete', ('g:briefy_finance', 'g:system')),
    )

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'customer', '_customer_user', 'pool',
            '_project_manager', 'external_id', '_customer_users', '_project_managers'
        ],
        'overrides': mixins.ProjectBriefyRoles.__colanderalchemy_config__['overrides']
    }

    customer_id = sa.Column(sautils.UUIDType,
                            sa.ForeignKey('customers.id'),
                            index=True,
                            nullable=False,
                            info={'colanderalchemy': {
                               'title': 'Customer',
                               'validator': colander.uuid,
                               'typ': colander.String}}
                            )
    """Customer ID.

    Builds the relation with :class:`briefy.leica.models.customer.Customer`.
    """

    abstract = sa.Column(
        'abstract',
        sa.Text,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Abstract',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Abstract for a project.

    Text field allowing a small, but meaningful description for an object.
    Used to store Bizdev comments.
    """

    order_type = sa.Column(
        sautils.ChoiceType(OrderTypeChoices, impl=sa.String()),
        default='order',
        nullable=False,
        info={
            'colanderalchemy': {
                'title': 'Type of Order',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Type of order the project support."""

    number_required_assets = sa.Column(sa.Integer(), default=10)
    """Number of required assets of a Project to be used in the Order as default value."""

    asset_types = sa.Column(
        JSONB,
        info={
            'colanderalchemy': {
                'title': 'Asset types.',
                'missing': colander.drop,
                'typ': schema.List()
            }
        }
    )
    """Asset types supported by this project.

    Options come from :mod:`briefy.leica.vocabularies.AssetTypes`.
    """

    @orm.validates('asset_types')
    def validate_asset_types(self, key, value):
        """Validate if values for asset_types are correct."""
        members = AssetTypes.__members__
        for item in value:
            if item not in members:
                raise ValidationError(message='Invalid type of asset', name=key)
        return value

    category = sa.Column(
        sautils.ChoiceType(CategoryChoices, impl=sa.String()),
        default='undefined',
        nullable=False
    )
    """Category of this Project.

    Options come from :mod:`briefy.common.vocabularies.categories`.
    """

    tech_requirements = sa.Column(
        sautils.JSONType,
        info={
            'colanderalchemy': {
                'title': 'Technical Requirements for this project.',
                'missing': colander.drop,
                'typ': schema.JSONType
            }
        }
    )
    """Technical requirements for orders in this project.

    It stores a dictionary of requirements to be fulfilled by each asset of each Assignment.

    i.e.  - for a project delivering only photos, its value might be::

        [
            {
                "asset_type": "Image",
                "set": {
                    "minimum_number": 10  # (aliased to 'minimum_number_of_photos' (deprecated))
                },
                "asset": {
                    "dimensions": [
                    {
                        "value": "4000x3000",
                        "operator": "min"
                    }
                    ],
                    "orientation": [
                    {
                        "value": "landscape",
                        "operator": "eq"
                    }
                    ]
                }
            },
            {
                "asset_type": "Video",
                "set": {
                    "minimum_number": 2
                },
                "asset": {
                    "duration": {"value": "30", "operator" :"min"}
                },
                "actions": [
                    {
                        "state": "post_processing",
                        "action": "copy",
                        "settings": {
                            "driver": "gdrive",
                            "parentId": "",
                            "subfolders": true,
                            "images": true,
                            "other": true,
                            "name": "order.customer_order_id",
                            "resize": []
                        }
                    },
                    ...
                ]
            },
            ...
        ]


    If there is a single asset type for the project, the outermost list may be omitted -
    and a single copy of the inner dictionary is used. The inner dictionary should
    have the keys "asset_type", "set" for validation constraints that apply to
    all assets of that type   taken together,
    and "asset" for denoting constraints for each asset of that type.

    (Deprecated: for compatibility reasons, ms.laure code will understand a
    missing "asset_type" key will default it to "Image".)
    """

    delivery = sa.Column(
        sautils.JSONType,
        default=DEFAULT_DELIVERY_CONFIG,
        info={
            'colanderalchemy': {
                'title': 'Delivery information for this project.',
                'missing': colander.drop,
                'typ': schema.JSONType
            }
        }
    )
    """Delivery configuration for orders in this project.

    It stores a dictionary of configurations to be used by the delivery mechanism.

    i.e::

        {
          "approve": {
            "archive": {
              "driver": "gdrive",
              "parentId": "",
              "subfolders": true,
              "images": true,
              "other": true,
              "name": "order.customer_order_id",
              "resize": []
            },
            "gdrive": {
              "driver": "gdrive",
              "parentId": "",
              "subfolders": false,
              "images": true,
              "other": false,
              "name": "order.customer_order_id",
              "resize": []
            },
          },
          "accept": {
            "sftp": {
              "driver": "sftp",
              "subfolders": false,
              "images": true,
              "other": false,
              "name": "order.customer_order_id",
              "resize": [
                {"name": "resized", "filter": "maxbytes": 4000000}
              ]
            }
          }
        }

    """

    cancellation_window = sa.Column(sa.Integer, default=1)
    """Period, in hours, before the shooting, an Assignment can be cancelled.

    i.e.: 24 would mean an Assignment in this project could be cancelled with
    at least 24 hour notice. Zero means no cancellation is possible.
    """

    availability_window = sa.Column(sa.Integer, default=6)
    """Period, in days, an availability date can be inputed.

    i.e.: 6 would mean an Order would have availability dates for, at least, 6 days in the future.
    Zero means no check is done.
    """

    approval_window = sa.Column(sa.Integer, default=5)
    """Period (business days), after the delivery, an Order has will be automatic accepted.

    If an Order is delivered and not rejected by customer it will be automatic accepted by a task.
    i.e.: 10 would mean an Order in this project could be approved up to 10 days after its delivery.
    Zero means a Order will be automatically approved.
    """

    add_order_roles = sa.Column(
        JSONB,
        default=DEFAULT_ADD_ORDER_ROLES,
        info={
            'colanderalchemy': {
                'title': 'Roles allowed to add an order.',
                'missing': colander.drop,
                'typ': schema.List()
            }
        }
    )
    """Roles allowed to add orders on this project.

    Options come from :mod:`briefy.common.vocabularies.roles.Groups`.
    """

    @orm.validates('add_order_roles')
    def validate_add_order_roles(self, key, value):
        """Validate if values for add_order_roles are correct."""
        all_groups = [item.value for item in Groups]
        for item in value:
            if item not in all_groups:
                raise ValidationError(message='Invalid role', name=key)
        return value

    @property
    def settings(self) -> Objectify:
        """Project settings.

        Aggregate settings information about a project.
        :return: Dictionary with all settings for a project.
        """
        # TODO: These settings are in a transitional state while
        # we move other configuration-related fields here.
        # To preserve backwards compability, we simply proxy those
        # fields - but their use should be deprecated as possible.

        # (NB. Even with Objectify, there is no provision
        # for write-back any of the "dates" subfields yet)

        return Objectify({
            'tech_requirements': self.tech_requirements,
            'delivery_config': self.delivery,
            'dates': {
                'cancellation_window': self.cancellation_window,
                'availability_window': self.availability_window,
                'approval_window': self.approval_window,
            },
            'permissions': {
                'add_order': self.add_order_roles
            }
        })

    @settings.setter
    def settings(self, value: t.Union[Objectify, t.Mapping]):
        """Project settings.

        Set all settings for a project.
        :value: Dictionary with all settings for a project.
        """
        # 'PUT' semmantics setter. This will destroy everything on the way.
        # to change a single sub-field, consider changing the just the desired
        # entry along with a call to
        # sqlalchemy.orm.attributes.flag_modified(obj, data_field_name)
        # (check the correct underlying field_name on the settings.getter
        # above while we are in this transitional stage)

        value = Objectify(value, sentinel=None)
        self.tech_requirements = value.tech_requirements or {}
        self.delivery = value.delivery_config or {}
        self.add_order_roles = value.permissions.add_order or []
        self.cancellation_window = value.dates.cancellation_window or 0
        self.availability_window = value.dates.availability_window or 0
        self.approval_window = value.dates.approval_window or 0

    orders = orm.relationship(
        'Order',
        backref=orm.backref('project'),
        lazy='dynamic'
    )
    """List of Orders of this project.

    Returns a collection of :class:`briefy.leica.models.job.order.Order`.
    """

    @sautils.aggregated('orders', sa.Column(sa.Integer, default=0))
    def total_orders(self):
        """Total Orders in this project.

        This attribute uses the Aggregated funcion of SQLAlchemy Utils, meaning the column
        should be updated on each change on any contained Order.
        """
        return sa.func.count('1')

    # Formerly known as brief
    briefing = sa.Column(
        sautils.URLType,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Briefing link',
                'validator': colander.url,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Path to briefing file regarding this Project."""

    release_template = sa.Column(
        sautils.URLType,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Release template',
                'validator': colander.url,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Path to release template file."""

    pool_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('pools.id'),
        index=True,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Pool ID',
                'validator': colander.uuid,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Pool ID.

    Relationship between a project and a Pool.
    """

    @cache_region.cache_on_arguments(should_cache_fn=enable_cache)
    def to_summary_dict(self) -> dict:
        """Return a summarized version of the dict representation of this Class.

        Used to serialize this object within a parent object serialization.
        :returns: Dictionary with fields and values used by this Class
        """
        data = super().to_summary_dict()
        return data

    @cache_region.cache_on_arguments(should_cache_fn=enable_cache)
    def to_listing_dict(self) -> dict:
        """Return a summarized version of the dict representation of this Class.

        Used to serialize this object within a parent object serialization.
        :returns: Dictionary with fields and values used by this Class
        """
        data = super().to_listing_dict()
        data['category'] = self.category.value \
            if isinstance(self.category, CategoryChoices) else self.category
        data['order_type'] = self.order_type.value \
            if isinstance(self.order_type, OrderTypeChoices) else self.order_type
        data = self._apply_actors_info(data)
        return data

    @cache_region.cache_on_arguments(should_cache_fn=enable_cache)
    def to_dict(self, excludes: list=None, includes: list=None):
        """Return a dict representation of this object."""
        excludes = list(excludes) if excludes else []
        excludes.append('orders')
        data = super().to_dict(excludes=excludes, includes=includes)
        data['slug'] = self.slug
        data['price'] = self.price
        data['category'] = self.category.value \
            if isinstance(self.category, CategoryChoices) else self.category
        data['order_type'] = self.order_type.value \
            if isinstance(self.order_type, OrderTypeChoices) else self.order_type
        data['settings'] = self.settings._get()
        data = self._apply_actors_info(data)
        if includes and 'state_history' in includes:
            # Workflow history
            add_user_info_to_state_history(self.state_history)
        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data


@event.listens_for(Project, 'after_update')
def project_after_update(mapper, connection, target):
    """Invalidate Project cache after instance update."""
    cache_region.invalidate(target)
