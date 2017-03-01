"""Briefy Leica Order to a Job."""
from briefy.common.db.types import AwareDateTime
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica import logger
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.descriptors import UnaryRelationshipWrapper
from briefy.leica.models.job import workflows
from briefy.leica.models.job.location import OrderLocation
from briefy.leica.models.project import Project
from briefy.leica.utils.transitions import get_transition_date_from_history
from briefy.leica.utils.user import add_user_info_to_state_history
from briefy.leica.vocabularies import OrderInputSource
from datetime import datetime
from dateutil.parser import parse
from sqlalchemy import orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import TimezoneType

import colander
import copy
import random
import sqlalchemy as sa
import sqlalchemy_utils as sautils
import string

__summary_attributes__ = [
    'id', 'title', 'description', 'slug', 'created_at', 'updated_at', 'state',
    'currency', 'price', 'number_required_assets', 'location', 'category',
    'timezone', 'scheduled_datetime', 'delivery', 'deliver_date', 'customer_order_id'
]

__listing_attributes__ = __summary_attributes__ + [
    'accept_date', 'availability', 'assignment', 'requirements', 'project', 'customer'
]

__colander_alchemy_config_overrides__ = \
    copy.copy(mixins.OrderBriefyRoles.__colanderalchemy_config__['overrides'])

# added to be able pass professional_id to the Order reassign transition
__colander_alchemy_config_overrides__.update(
    dict(
        professional_id={
            'title': 'Professional ID',
            'missing': colander.drop,
            'typ': colander.String()
        },
        payout_value={
            'title': 'Payout Value',
            'missing': colander.drop,
            'typ': colander.Integer()
        },
        payout_currency={
            'title': 'Payout Currency',
            'missing': colander.drop,
            'typ': colander.String()
        },
        travel_expenses={
            'title': 'Travel Expenses',
            'missing': colander.drop,
            'typ': colander.Integer()
        }
    )
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
    __summary_attributes_relations__ = [
        'project', 'comments', 'customer', 'assignment', 'assignments'
    ]
    __listing_attributes__ = __listing_attributes__

    __raw_acl__ = (
        ('create', ('g:briefy_pm', 'g:briefy_finance', 'g:briefy_bizdev', 'g:system')),
        ('list', ('g:briefy_qa', 'g:briefy_bizdev',
                  'g:briefy_scout', 'g:briefy_finance', 'g:system')),
        ('view', ('g:briefy_qa', 'g:briefy_bizdev',
                  'g:briefy_scout', 'g:briefy_finance', 'g:system')),
        ('edit', ('g:briefy_pm', 'g:briefy_finance', 'g:briefy_bizdev', 'g:system')),
        ('delete', ('g:briefy_finance', 'g:system')),
    )

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'project', 'comments', 'customer',
            '_project_manager', '_scout_manager', '_customer_user', 'external_id',
            'assignment', 'assignments', '_project_managers', '_scout_managers',
            '_customer_users',
        ],
        'overrides': __colander_alchemy_config_overrides__

    }

    __versioned__ = {
        'exclude': ['state_history', '_state_history', 'scheduled_datetime', 'timezone']
    }
    """SQLAlchemy Continuum settings.

    By default we do not keep track of state_history and helper columns.
    """

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
        backref=orm.backref('active_order'),
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

    scheduled_datetime = sa.Column(
        AwareDateTime(),
        nullable=True,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Scheduled date for shooting',
                'missing': colander.drop,
                'typ': colander.DateTime
            }
        }
    )
    """Scheduled date time of shooting."""

    deliver_date = sa.Column(
        AwareDateTime(),
        nullable=True,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Delivery date',
                'missing': colander.drop,
                'typ': colander.DateTime
            }
        }
    )
    """Delivery date of this Order."""

    last_deliver_date = sa.Column(
        AwareDateTime(),
        nullable=True,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Delivery date',
                'missing': colander.drop,
                'typ': colander.DateTime
            }
        }
    )
    """Last delivery date of this Order."""

    accept_date = sa.Column(
        AwareDateTime(),
        nullable=True,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Acceptance date',
                'missing': colander.drop,
                'typ': colander.DateTime
            }
        }
    )
    """Acceptance date of this Order."""

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
        project = self.project
        timezone = self.timezone

        if value and value[0] == value[1]:
            msg = 'Availability dates should be different.'
            raise ValueError(msg)

        if value and timezone and project:
            availability_window = project.availability_window
            now = datetime.now(tz=timezone)
            for availability in value:
                availability = parse(availability)
                availability = availability.astimezone(timezone)
                date_diff = availability - now
                if date_diff.days < availability_window:
                    msg = 'Both availability dates must be at least {window} days from now.'
                    msg = msg.format(window=availability_window)
                    raise ValueError(msg)
        elif value:
            logger.warn('Could not check availability dates. Order {id}'.format(self.id))

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

        IMPORTANT: This difers from project tech_requirements - those
        are wrapped in the 'asset' key issued from here.

        :return: A dictionary with technical requirements for an Order.
        """
        project = self.project
        requirements = project.tech_requirements or {}
        return requirements

    timezone = sa.Column(TimezoneType(backend='pytz'), default='UTC')
    """Timezone in which this address is located.

    i.e.: UTC, Europe/Berlin
    """
    # Deal with timezone changes
    @sautils.observes('_location.timezone')
    def _timezone_observer(self, timezone):
        """Update timezone on this object."""
        if timezone:
            self.timezone = timezone
            for assignment in self.assignments:
                assignment.timezone = timezone

    def _update_dates_from_history(self, keep_updated_at: bool = False):
        """Update dates from history."""
        updated_at = self.updated_at
        state_history = self.state_history

        def updated_if_changed(attr, t_list, first=False):
            """Update only if changed."""
            existing = getattr(self, attr)
            new = get_transition_date_from_history(
                t_list, state_history, first=first
            )
            if new != existing:
                setattr(self, attr, new)

        # Set first deliver date
        transitions = ('deliver',)
        updated_if_changed('deliver_date', transitions, True)

        # Set last deliver date
        transitions = ('deliver',)
        updated_if_changed('last_deliver_date', transitions, False)

        # Set acceptance date
        transitions = ('accept', 'refuse')
        updated_if_changed('accept_date', transitions, False)

        if keep_updated_at:
            self.updated_at = updated_at

    # Deal with assignment changes
    @sautils.observes('assignment.scheduled_datetime')
    def _scheduled_datetime_observer(self, scheduled_datetime):
        """Update scheduled_datetime on this object."""
        existing = self.scheduled_datetime
        if scheduled_datetime != existing:
            self.scheduled_datetime = scheduled_datetime

    # Relevant dates
    @sautils.observes('state')
    def _dates_observer(self, state):
        """Calculate dates on a change of a state."""
        # Update all dates
        self._update_dates_from_history()

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
        data = super().to_dict(excludes=['assignment', 'assignments'])

        assignment = self.assignment
        assignment_data = None
        if assignment:
            assignment_data = self.assignment.to_summary_dict()
            assignment_data = self._apply_actors_info(assignment_data, assignment)

        data['description'] = self.description
        data['briefing'] = self.project.briefing
        data['availability'] = self.availability
        data['price'] = self.price
        data['slug'] = self.slug
        data['deliver_date'] = self.deliver_date
        data['scheduled_datetime'] = self.deliver_date
        data['delivery'] = self.delivery
        data['location'] = self.location.to_summary_dict() if self.location else None
        data['timezone'] = self.timezone
        data['assignment'] = assignment_data
        data['assignments'] = [item.to_summary_dict() for item in self.assignments]
        data['tech_requirements'] = self.tech_requirements
        # Workflow history
        add_user_info_to_state_history(self.state_history)

        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data
