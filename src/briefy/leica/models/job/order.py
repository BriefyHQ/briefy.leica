"""Briefy Leica Order to a Job."""
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.descriptors import UnaryRelationshipWrapper
from briefy.leica.models.job import workflows
from briefy.leica.models.project import Project
from briefy.leica.utils.transitions import get_transition_date
from briefy.leica.models.job.location import OrderLocation
from briefy.leica.vocabularies import OrderInputSource
from briefy.leica.utils.user import add_user_info_to_state_history
from datetime import datetime
from sqlalchemy import orm
from sqlalchemy.ext.hybrid import hybrid_property

import colander
import copy
import random
import sqlalchemy as sa
import sqlalchemy_utils as sautils
import string

__summary_attributes__ = [
    'id', 'title', 'description', 'slug', 'created_at', 'updated_at', 'state',
    'price', 'number_required_assets', 'location', 'category'
]

__listing_attributes__ = __summary_attributes__ + [
    'customer_order_id', 'deliver_date', 'accept_date', 'availability', 'assignment',
    'requirements', 'delivery', 'project', 'customer', 'timezone'
]

__colander_alchemy_config_overrides__ = \
    copy.copy(mixins.OrderBriefyRoles.__colanderalchemy_config__['overrides'])

# added to be able pass professional_id to the Order reassign transition
__colander_alchemy_config_overrides__.update(
    {'professional_id': {
        'title': 'Professional ID',
        'missing': colander.drop,
        'typ': colander.String()
    }}
)


def create_order_slug():
    """Create slug ID for the Order."""
    dt = datetime.now()
    part1 = '{:s}{:02d}'.format(str(dt.year)[-2:], dt.month)
    part2 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3))
    part3 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3))
    return '-'.join((part1, part2, part3))


def get_customer_id_from_project(context):
    """Get customer_id for Order from the Project.customer_id."""
    project_id = context.current_parameters.get('project_id')
    project = Project.get(project_id)
    return project.customer_id


def get_category_from_project(context):
    """Get category for Order from the Project.category."""
    project_id = context.current_parameters.get('project_id')
    project = Project.get(project_id)
    return project.category


class Order(mixins.OrderFinancialInfo, mixins.OrderBriefyRoles,
            mixins.KLeicaVersionedMixin, Base):
    """An Order from the customer."""

    _workflow = workflows.OrderWorkflow

    __summary_attributes__ = __summary_attributes__
    __summary_attributes_relations__ = ['project', 'comments', 'customer', 'assignment']
    __listing_attributes__ = __listing_attributes__

    __raw_acl__ = (
        ('create', ('g:briefy_pm', 'g:briefy_finance', 'g:briefy_bizdev', 'g:system')),
        ('list', ('g:briefy', 'g:system')),
        ('view', ('g:briefy', 'g:system')),
        ('edit', ('g:briefy_pm', 'g:briefy_finance', 'g:briefy_bizdev', 'g:system')),
        ('delete', ('g:briefy_finance', 'g:system')),
    )

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'project', 'comments', 'customer',
            '_project_manager', '_scout_manager', '_customer_user', 'external_id',
            'assignment', 'assignments',
        ],
        'overrides': __colander_alchemy_config_overrides__

    }

    _slug = sa.Column('slug',
                      sa.String(255),
                      nullable=True,
                      index=True,
                      default=create_order_slug,
                      info={'colanderalchemy': {
                          'title': 'Description',
                          'typ': colander.String}}
                      )
    """Slug -- friendly id -- for the object.

    To be used in url and as human readable ID. (this should be generated by an Order)
    """

    @hybrid_property
    def slug(self) -> str:
        """Return a slug for an object.

        :return: A slug to be added to an url.
        """
        return self._slug

    @slug.setter
    def slug(self, value: str):
        """Set a new slug for this object.

        If the value is None, we generate a new one using
        :func:`briefy.common.utils.data.generate_contextual_slug`
        :param value: Value of the new slug
        """
        if self._slug:
            raise Exception('Slug should not be changed.')
        else:
            self._slug = value

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

    job_id = sa.Column(
        sa.String,
        nullable=True,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Internal Job ID (deprecated)',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Order ID was the main Briefy id for an Order.

    This field was used on Knack as an auto-incremented field named 'internal_job_id'.
    """

    # Customer
    customer_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('customers.id'),
        index=True,
        default=get_customer_id_from_project,
        nullable=False,
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
        index=True,
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
        default=get_category_from_project,
        nullable=False
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

    number_required_assets = sa.Column(
        sa.Integer(),
        default=10
    )
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
        order_by='asc(Assignment.created_at)',
        backref=orm.backref('order')
    )
    """Assignments.

    Relationship with :class:`briefy.leica.models.job.Assignment`.
    """

    assignment = orm.relationship(
        'Assignment',
        uselist=False,
        viewonly=True,
        order_by='desc(Assignment.created_at)',
        primaryjoin='''and_(
            Order.id == Assignment.order_id,
            not_(Assignment.state.in_(('cancelled', 'perm_reject')))
        )''',
    )
    """Current Assignment connect to this order.

    Collection of :class:`briefy.leica.models.job.Assignment`.
    """

    """ # TODO: enable this!
    _tech_requirements = sa.Column(
        sautils.JSONType,
        info={
            'colanderalchemy': {
                'title': 'Technical Requirements for this assignemnt.',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """
    """Technical requirements for orders in this order.

    It stores a dictionary of requirements to be fulfilled by each asset of each Assignment.
    If missing, the Project's technical requirements are used in its place.
    """

    _availability = sa.Column(
        'availability',
        sautils.JSONType,
        info={
            'colanderalchemy': {
                'title': 'Availability for scheduling this Order.',
                'missing': colander.drop,
                'typ': colander.List
            }
        }
    )
    """Availability attribute.

    Access to it should be done using the hybrid_property availability.
    """

    comments = orm.relationship(
        'Comment',
        foreign_keys='Comment.entity_id',
        order_by='desc(Comment.created_at)',
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
        return availability

    @availability.setter
    def availability(self, value: list):
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
        # TODO: enable this:
        # if self._tech_requirements:
        #     requirements = self._tech_requirements
        # else:
        #     requirements = self.project.tech_requirements
        project = self.project
        requirements = self.project.tech_requirements or {}

        # The tech requirements is composed with the required
        # number of photos pr project or per order:
        all_requirements = {
            'set': {
                'minimum_number_of_photos': project.number_required_assets
                # Due to development constraints.
                # In the future this should come from
                # self.number_required_assets
            },
        }
        all_requirements.update(requirements)
        return all_requirements

    @hybrid_property
    def timezone(self) -> str:
        """Return Timezone for this order.

        Information will be obtained from main location.
        """
        location = self.location
        return location.timezone

    @hybrid_property
    def deliver_date(self) -> datetime:
        """Return last deliver date for this Orders.

        Information will be extracted from state history field.
        """
        transitions = ('deliver',)
        return get_transition_date(transitions, self, first=False)

    @hybrid_property
    def accept_date(self) -> datetime:
        """Return first accepted or refused date for this Order.

        Information will be extracted from state history field.
        """
        transitions = ('accept', 'refuse')
        return get_transition_date(transitions, self, first=True)

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
        data = super().to_dict()
        data['description'] = self.description
        data['briefing'] = self.project.briefing
        data['availability'] = self.availability
        data['price'] = self.price
        data['slug'] = self.slug
        data['deliver_date'] = self.deliver_date
        data['delivery'] = self.delivery
        data['location'] = self.location
        data['timezone'] = self.timezone
        data['assignment'] = self.assignment.to_summary_dict() if self.assignment else None
        data['tech_requirements'] = self.tech_requirements
        # Workflow history
        add_user_info_to_state_history(self.state_history)

        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data
