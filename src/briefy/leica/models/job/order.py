"""Briefy Leica Order to a Job."""
from briefy.common.db.types import AwareDateTime
from briefy.common.utils import schema
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica import logger
from briefy.leica.cache import cache_manager
from briefy.leica.cache import cache_region
from briefy.leica.cache import enable_cache
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.descriptors import UnaryRelationshipWrapper
from briefy.leica.models.job import workflows
from briefy.leica.models.job.location import OrderLocation
from briefy.leica.models.project import Project
from briefy.leica.utils.transitions import get_transition_date_from_history
from briefy.leica.utils.user import add_user_info_to_state_history
from briefy.leica.vocabularies import AssetTypes
from briefy.leica.vocabularies import OrderInputSource
from briefy.ws.errors import ValidationError
from datetime import datetime
from dateutil.parser import parse
from sqlalchemy import event
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy_utils import TimezoneType

import colander
import copy
import pytz
import random
import sqlalchemy as sa
import sqlalchemy_utils as sautils
import string


__summary_attributes__ = [
    'id', 'title', 'description', 'slug', 'created_at', 'updated_at', 'state',
    'price_currency', 'price', 'number_required_assets', 'location', 'category',
    'timezone', 'scheduled_datetime', 'delivery', 'deliver_date', 'customer_order_id'
]

__listing_attributes__ = __summary_attributes__ + [
    'accept_date', 'availability', 'assignment', 'requirements', 'project',
    'customer', 'refused_times', 'asset_types', 'type', 'current_type'
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
        },
        additional_compensation={
            'title': 'Additional Compensation',
            'missing': colander.drop,
            'typ': colander.Integer()
        },
        reason_additional_compensation={
            'title': 'Reason Additional Compensation',
            'missing': colander.drop,
            'typ': colander.String()
        }
    )
)


def create_order_slug():
    """Create slug ID for the Order."""
    dt = datetime.now()
    part1 = '{0:s}{1:02d}'.format(str(dt.year)[-2:], dt.month)
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


def default_actual_order_price(context):
    """Get category for Order from the Project.category."""
    order_type = context.current_parameters.get('type')
    actual_order_price = 0
    if order_type == 'order':
        # TODO: this can be zero if price not informed
        # The subscriber also take care of this on the order and leadorder creation
        actual_order_price = context.current_parameters.get('price', 0)
    return actual_order_price


def default_current_type(context):
    """Get current type ."""
    return context.current_parameters.get('type')


class Order(mixins.OrderFinancialInfo, mixins.OrderBriefyRoles,
            mixins.KLeicaVersionedMixin, Base):
    """An Order from the customer."""

    _workflow = workflows.OrderWorkflow

    __summary_attributes__ = __summary_attributes__
    __summary_attributes_relations__ = [
        'project', 'comments', 'customer', 'assignment', 'assignments', 'location'
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
            'state_history', 'state', 'project', 'comments', 'customer', 'type',
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

    type = sa.Column(sa.String(50))
    """Polymorphic type name."""

    @declared_attr
    def __mapper_args__(cls):
        """Return polymorphic identity."""
        cls_name = cls.__name__.lower()
        args = {
            'polymorphic_identity': cls_name,
        }
        if cls_name == 'order':
            args['polymorphic_on'] = cls.type
        return args

    current_type = sa.Column(
        sa.String(50),
        index=True,
        default=default_current_type,
    )
    """Type of the Order during its life cycle."""

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

    refused_times = sa.Column(
        sa.Integer(),
        default=0
    )
    """Number times the Order was refused."""

    requirements = sa.Column(sa.Text, default='')
    """Human-readable requirements for an Order."""

    actual_order_price = sa.Column(
        'actual_order_price',
        sa.Integer,
        nullable=True,
        default=default_actual_order_price,
        info={
            'colanderalchemy': {
                'title': 'Acutal Order Price',
                'missing': None,
                'typ': colander.Integer
            }
        }
    )
    """Price to be paid, by the customer, for this order.

    Amount to be paid by the customer for this order.
    For Orders this value will be the same of Order.price, on creation.
    For LeadOrders this value will be 0.

    This value is expressed in cents.
    """

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
        primaryjoin="""and_(
            Order.id == Assignment.order_id,
            not_(Assignment.state.in_(('cancelled', 'perm_reject')))
        )""",
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

    asset_types = sa.Column(
        JSONB,
        info={
            'colanderalchemy': {
                'title': 'Asset types.',
                'missing': colander.drop,
                'typ': schema.List(),
            }
        }
    )
    """Asset types supported by this order.

    Options come from :mod:`briefy.leica.vocabularies.AssetTypes`.
    """

    @orm.validates('asset_types')
    def validate_asset_types(self, key, value):
        """Validate if values for asset_types are correct."""
        max_types = 1
        if len(value) > max_types:
            raise ValidationError(message='Invalid number of type of assets', name=key)
        members = AssetTypes.__members__
        for item in value:
            if item not in members:
                raise ValidationError(message='Invalid type of asset', name=key)
        return value

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
        if isinstance(timezone, str):
            timezone = pytz.timezone(timezone)
        user = self.workflow.context
        not_pm = 'g:briefy_pm' not in user.groups if user else True
        validated_value = []

        if value and len(value) != len(set(value)):
            msg = 'Availability dates should be different.'
            raise ValidationError(message=msg, name='availability')

        if value and timezone and project:
            if not_pm:
                availability_window = project.availability_window
            else:
                # allow less than 24hs for PMs but not in the past
                availability_window = 0
            now = datetime.now(tz=timezone)
            for availability in value:
                if isinstance(availability, str):
                    availability = parse(availability)
                tz_availability = availability.astimezone(timezone)
                date_diff = tz_availability - now
                if date_diff.days < availability_window:
                    msg = 'Both availability dates must be at least {window} days from now.'
                    msg = msg.format(window=availability_window)
                    raise ValidationError(message=msg, name='availability')

                validated_value.append(availability.isoformat())
        elif value:
            logger.warn('Could not check availability dates. Order {id}'.format(id=self.id))

        self._availability = validated_value if validated_value else value

    _delivery = sa.Column(
        'delivery',
        sautils.JSONType,
        info={
            'colanderalchemy': {
                'title': 'Delivery information.',
                'missing': colander.drop,
                'typ': schema.JSONType
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

        (Do not confuse this attribute with project.delivery which contains information on
        how to deliver the assets)
        """
        delivery = self._delivery
        return delivery

    @delivery.setter
    def delivery(self, value: dict):
        """Set delivery information for an Order."""
        self._delivery = value
        # Ensure the correct key is updated and object is set as dirty
        flag_modified(self, '_delivery')

    # TODO: If on the future there is the need to override project.delivery
    # for specific orders, create an order.delivery_info JSON field
    # which will override the information on project.delivery
    # There is partial support for an eventual order.delivery.info attribute on ms.laure

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

        def number_of_transitions(transition_name):
            """Return the number of times one transition happened."""
            total = [t for t in state_history if t['transition'] == transition_name]
            return len(total)

        # updated refused times
        self.refused_times = number_of_transitions('refuse')

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
        if scheduled_datetime and scheduled_datetime != existing:
            self.scheduled_datetime = scheduled_datetime

    # Relevant dates
    @sautils.observes('state')
    def _dates_observer(self, state):
        """Calculate dates on a change of a state."""
        # Update all dates
        self._update_dates_from_history()

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
        data = super().to_dict(excludes=excludes, includes=includes)
        assignment_data = None
        if self.assignments:
            assignment = self.assignments[-1]
            assignment_data = assignment.to_summary_dict()
            assignment_data = self._apply_actors_info(assignment_data, assignment)

        data['description'] = self.description
        data['briefing'] = self.project.briefing
        data['availability'] = self.availability
        data['price'] = self.price
        data['slug'] = self.slug
        data['source'] = self.source.value \
            if isinstance(self.source, OrderInputSource) else self.source
        data['category'] = self.category.value \
            if isinstance(self.category, CategoryChoices) else self.category
        data['deliver_date'] = self.deliver_date
        data['scheduled_datetime'] = self.deliver_date
        data['delivery'] = self.delivery
        data['location'] = self.location.to_summary_dict() if self.location else None
        data['timezone'] = self.timezone
        data['assignment'] = assignment_data
        data['assignments'] = [item.to_summary_dict() for item in self.assignments]
        data['tech_requirements'] = self.tech_requirements

        add_user_info_to_state_history(self.state_history)
        if includes and 'state_history' in includes:
            # Workflow history
            add_user_info_to_state_history(self.state_history)

        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data


@event.listens_for(Order, 'after_update')
def order_after_update(mapper, connection, target):
    """Invalidate Order cache after instance update."""
    cache_manager.refresh(target)
    for assignment in target.assignments:
        cache_manager.refresh(assignment)
