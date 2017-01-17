"""Briefy Leica Order to a Job."""
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.descriptors import UnaryRelationshipWrapper
from briefy.leica.models.job import workflows
from briefy.leica.models.job.location import OrderLocation
from briefy.leica.vocabularies import OrderInputSource
from briefy.ws.utils.user import add_user_info_to_state_history
from sqlalchemy import orm
from sqlalchemy.ext.hybrid import hybrid_property

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils

__summary_attributes__ = [
    'id', 'title', 'description', 'slug', 'created_at', 'updated_at', 'state',
    'price', 'number_required_assets', 'location', 'category'
]

__listing_attributes__ = __summary_attributes__


class Order(mixins.OrderFinancialInfo, mixins.OrderBriefyRoles,
            mixins.KLeicaVersionedMixin, Base):
    """An Order from the customer."""

    _workflow = workflows.OrderWorkflow

    __summary_attributes__ = __summary_attributes__
    __summary_attributes_relations__ = ['project', 'comments', 'customer']
    __listing_attributes__ = __listing_attributes__

    __raw_acl__ = (
        ('list', ('l:customer', 'g:briefy_qa', 'g:briefy_bizdev', 'g:briefy_pm', 'g:system')),
        ('view', ()),
        ('edit', ()),
        ('delete', ()),
    )

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'project', 'comments', 'customer',
            '_project_manager', '_scout_manager', '_customer_user'
        ]
    }

    customer_order_id = sa.Column(
        sa.String,
        default='',
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Customer Order ID',
                'typ': colander.String
            }
        }
    )
    """Customer Order ID.

    Reference for the customer to find this order. On Knack this field was refered as 'job_id'
    """

    job_id = sa.Column(sa.String, nullable=True, index=True)
    """Order ID was the main Briefy id for an Order.

    This field was used on Knack as an auto-incremented field named 'internal_job_id'.
    """

    # Customer
    customer_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('customers.id'),
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Customer ID',
                'validator': colander.uuid,
                'missing': None,
                'typ': colander.String
            }
        }
    )
    """Customer ID.

    Relationship with :class:`briefy.leica.models.customer.Customer`.
    """

    # Project
    project_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('projects.id'),
        nullable=False,
        info={
            'colanderalchemy': {
                'title': 'Project ID',
                'validator': colander.uuid,
                'missing': None,
                'typ': colander.String
            }
        }
    )
    """Project ID.

    Relationship with :class:`briefy.leica.models.project.Project`.
    """

    category = sa.Column(
        sautils.ChoiceType(CategoryChoices, impl=sa.String()),
        default='undefined',
        nullable=True
    )
    """Category of this Order.

    Options come from :mod:`briefy.common.vocabularies.categories`.
    """

    source = sa.Column(
        sautils.ChoiceType(OrderInputSource, impl=sa.String()),
        default='briefy',
        nullable=False
    )
    """Source of this Order.

    This field stores which part created this Order, Customer or Briefy.
    Options come from :mod:`briefy.leica.vocabularies`.
    """

    number_required_assets = sa.Column(sa.Integer(), default=10)
    """Number of required assets of an Order."""

    requirements = sa.Column(sa.Text, default='')
    """Human-readable requirements for an Order."""

    _location = orm.relationship(
        'OrderLocation',
        uselist=False,
        backref=orm.backref('order'),
        info={
            'colanderalchemy': {
                'title': 'Location',
                'missing': colander.drop
            }
        }
    )
    """Order Location.

    Relationship with :class:`briefy.leica.models.job.location.OrderLocation`.
    """

    location = UnaryRelationshipWrapper('_location', OrderLocation, 'order_id')
    """Descriptor to handle location get, set and delete."""

    # Assignments
    assignments = orm.relationship(
        'Assignment',
        backref=orm.backref('order')
    )
    """Assignments.

    Relationship with :class:`briefy.leica.models.job.Assignment`.
    """

    _availability = sa.Column(
        'availability',
        sautils.JSONType,
        info={
            'colanderalchemy': {
                'title': 'Availability for scheduling this Order.',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Availability attribute.

    Access to it should be done using the hybrid_property availability.
    """

    comments = orm.relationship(
        'Comment',
        foreign_keys='Comment.entity_id',
        order_by='asc(Comment.created_at)',
        primaryjoin='Comment.entity_id == Order.id',
        lazy='dynamic'
    )
    """Comments connected to this order.

    Collection of :class:`briefy.leica.models.comment.Comment`.
    """

    @hybrid_property
    def availability(self) -> list:
        """Return availability for an Order.

        This should return a list with zero or more available dates for
        scheduling this Order.
        i.e.::

            [
              datetime(2016, 12, 21, 12, 0, 0),
              datetime(2016, 12, 22, 14, 0, 0),
            ]

        """
        availability = self._availability
        if isinstance(availability, dict):
            availability = [availability, ]
        return availability

    @availability.setter
    def availability(self, value: dict):
        """Set availabilities for an Order."""
        self._availability = value

    _delivery = sa.Column(
        'delivery',
        sautils.JSONType,
        info={
            'colanderalchemy': {
                'title': 'Delivery information.',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Delivery links.

    JSON with a collection of delivery links. Should be accessed using the 'delivery' attribute.
    """

    @hybrid_property
    def delivery(self) -> dict:
        """Return delivery info for an Order.

        This should return a dict with the delivery method and URL
        i.e.::

            {
                'sftp': 'sftp://agoda@delivery.briefy.co/bali/3456/',
                'gdrive': 'https://drive.google.com/foo/bar',
            }

        """
        delivery = self._delivery
        return delivery

    @delivery.setter
    def delivery(self, value: dict):
        """Set delivery information for an Order."""
        self._delivery = value

    @property
    def assets(self):
        """Return Assets from this Order.

        Collection of :class:`briefy.leica.models.asset.Asset`.
        """
        from briefy.leica.models.asset import Asset
        query = Asset.query().filter(
                Asset.c.job_id.in_([a.id for a in self.assignments if a.state == 'approved']),
        )
        return query

    @property
    def tech_requirements(self) -> dict:
        """Tech requirements for this Order.

        :return: A dictionary with technical requirements for an Order.
        """
        project = self.project
        return project.tech_requirements

    def to_listing_dict(self) -> dict:
        """Return a summarized version of the dict representation of this Class.

        Used to serialize this object within a parent object serialization.
        :returns: Dictionary with fields and values used by this Class
        """
        data = super().to_listing_dict()
        data = self._apply_actors_info(data)
        return data

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict(excludes=['internal_comments'])
        data['description'] = self.description
        data['briefing'] = self.project.briefing
        data['availability'] = self.availability
        data['price'] = self.price
        data['slug'] = self.slug
        data['location'] = self.location

        # Workflow history
        add_user_info_to_state_history(self.state_history)

        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data
