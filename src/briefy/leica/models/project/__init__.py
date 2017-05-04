"""Briefy Leica Project model."""
from briefy.common.db.mixins import BriefyRoles
from briefy.common.utils import schema
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica.cache import cache_region
from briefy.leica.cache import enable_cache
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.project import workflows
from briefy.leica.utils.user import add_user_info_to_state_history
from sqlalchemy import event
from sqlalchemy import orm
from zope.interface import implementer
from zope.interface import Interface

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


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
        'id', 'title', 'description', 'created_at', 'updated_at', 'state', 'slug'
    ]

    __summary_attributes_relations__ = ['customer', 'pool']

    __listing_attributes__ = [
        'id', 'title', 'description', 'created_at', 'updated_at', 'state',
        'external_id', 'total_orders', 'slug', 'customer'
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

    number_required_assets = sa.Column(sa.Integer(), default=10)
    """Number of required assets of a Project to be used in the Order as default value."""

    category = sa.Column(
        sautils.ChoiceType(CategoryChoices, impl=sa.String()),
        default='undefined',
        nullable=False
    )
    """Category of this Order.

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

    It stores a dictionary of requirements to be full filed by each asset of each Assignment.
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
        data['category'] = self.category.value \
            if isinstance(self.category, CategoryChoices) else self.category
        data = self._apply_actors_info(data)
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
        data = self._apply_actors_info(data)
        add_user_info_to_state_history(self.state_history)
        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data


@event.listens_for(Project, 'after_update')
def project_after_update(mapper, connection, target):
    """Invalidate Project cache after instance update."""
    cache_region.invalidate(target)
