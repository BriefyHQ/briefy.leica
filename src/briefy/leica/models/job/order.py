"""Briefy Leica Order model."""
from briefy.common.db import datetime_utcnow
from briefy.common.db.models import Item
from briefy.common.db.types import AwareDateTime
from briefy.common.utils import schema
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica import logger
from briefy.leica.cache import cache_manager
from briefy.leica.cache import cache_region
from briefy.leica.cache import enable_cache
from briefy.leica.models import mixins
from briefy.leica.models.descriptors import UnaryRelationshipWrapper
from briefy.leica.models.job import workflows
from briefy.leica.models.job.location import OrderLocation
from briefy.leica.models.project import Project
from briefy.leica.models.types import TimezoneType
from briefy.leica.utils.charges import order_charges_update
from briefy.leica.utils.transitions import get_transition_date_from_history
from briefy.leica.utils.user import add_user_info_to_state_history
from briefy.leica.vocabularies import AssetTypes
from briefy.leica.vocabularies import OrderChargesChoices
from briefy.leica.vocabularies import OrderInputSource
from briefy.ws.errors import ValidationError
from datetime import datetime
from dateutil.parser import parse
from sqlalchemy import event
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.attributes import flag_modified

import colander
import copy
import pytz
import random
import sqlalchemy as sa
import sqlalchemy_utils as sautils
import string
import typing as t


__summary_attributes__ = [
    'id', 'title', 'description', 'slug', 'created_at', 'updated_at', 'state',
    'price_currency', 'price', 'number_required_assets', 'location', 'category',
    'timezone', 'scheduled_datetime', 'delivery', 'deliver_date', 'customer_order_id',
    'requirement_items'
]

__listing_attributes__ = __summary_attributes__ + [
    'accept_date', 'availability', 'assignment', 'requirements', 'project',
    'customer', 'refused_times', 'asset_types', 'current_type', 'scheduled_datetime'
]

__colander_alchemy_config_overrides__ = \
    copy.copy(mixins.OrderRolesMixin.__colanderalchemy_config__['overrides'])

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
    current_type = context.current_parameters.get('current_type')
    default_price = 0
    actual_order_price = 0
    if current_type == 'order':
        project_id = context.current_parameters.get('project_id', None)
        if project_id:
            project = Project.get(project_id)
            default_price = project.price if project else default_price
        actual_order_price = context.current_parameters.get('price', default_price)
    return actual_order_price


def default_current_type(context):
    """Get current type ."""
    return context.current_parameters.get('type')


_order_charges_choices = [f for f in OrderChargesChoices.__members__.keys()]


class OrderCharge(colander.MappingSchema):
    """An additional charge to an Order."""

    id = colander.SchemaNode(colander.String(), validator=colander.uuid, missing='')
    category = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf(_order_charges_choices)
    )
    amount = colander.SchemaNode(colander.Int())
    reason = colander.SchemaNode(colander.String(), missing='')
    created_at = colander.SchemaNode(colander.DateTime(), missing='')
    created_by = colander.SchemaNode(colander.String(), validator=colander.uuid)
    invoice_number = colander.SchemaNode(colander.String(), missing='')
    invoice_date = colander.SchemaNode(colander.Date(), missing='')


class OrderCharges(colander.SequenceSchema):
    """Collection of charges for an Order."""

    charge = OrderCharge()


class RequirementItem(colander.MappingSchema):
    """Specific requirement item of an Order."""

    id = colander.SchemaNode(colander.String(), validator=colander.uuid, missing='')
    category = colander.SchemaNode(colander.String())
    min_number_assets = colander.SchemaNode(colander.Int())
    description = colander.SchemaNode(colander.String(), missing='')
    tags = colander.SchemaNode(colander.List())
    created_at = colander.SchemaNode(colander.DateTime(), missing='')
    created_by = colander.SchemaNode(colander.String(), validator=colander.uuid)
    folder_id = colander.SchemaNode(colander.String(), missing=colander.drop)
    parent_folder_id = colander.SchemaNode(colander.String(), missing=colander.drop)
    folder_name = colander.SchemaNode(colander.String(), missing=colander.drop)


class RequirementItems(colander.SequenceSchema):
    """Collection of specific requirement items of an Order."""

    items = RequirementItem()


class Order(mixins.OrderFinancialInfo, mixins.LeicaSubVersionedMixin, mixins.OrderRolesMixin, Item):
    """An Order from the customer."""

    _workflow = workflows.OrderWorkflow

    __summary_attributes__ = __summary_attributes__
    __summary_attributes_relations__ = [
        'assignment', 'assignments', 'customer', 'project', 'location'
    ]
    __listing_attributes__ = __listing_attributes__

    __exclude_attributes__ = ['comments']

    __to_dict_additional_attributes__ = [
        'availability', 'delivery', 'tech_requirements', 'price'
    ]

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
            '_project_manager', '_scout_manager', '_customer_user',
            'assignment', 'assignments', '_project_managers', '_scout_managers',
            '_customer_users', 'total_order_price'
        ],
        'overrides': __colander_alchemy_config_overrides__

    }

    __versioned__ = {
        'exclude': ['state_history', '_state_history', 'scheduled_datetime', 'timezone']
    }
    """SQLAlchemy Continuum settings.

    By default we do not keep track of state_history and helper columns.
    """

    __parent_attr__ = 'project_id'

    current_type = sa.Column(
        sa.String(50),
        index=True,
        default=default_current_type,
    )
    """Type of the Order during its life cycle."""

    @classmethod
    def create(cls, payload: dict) -> 'Item':
        """Factory that creates a new instance of this object.

        :param payload: Dictionary containing attributes and values
        :type payload: dict
        """
        payload['slug'] = create_order_slug()
        return super().create(payload)

    @Item.slug.setter
    def slug(self, value: str):
        """Set a new slug for this object.

        Generate a slug using :func:`create_order_slug`
        :param value: Value of the new slug, if passed, will raise an Exception.
        """
        if value and self.slug:
            raise Exception('Order slug should never be updated.')
        elif value:
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

    project = orm.relationship(
        'Project',
        foreign_keys='Order.project_id'
    )
    """Project.

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

    refused_times = sa.Column(
        sa.Integer(),
        default=0
    )
    """Number times the Order was refused."""

    requirement_items = sa.Column(
        JSONB,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Requirement Items',
                'typ': colander.List,
                'missing': None,
            }
        }
    )
    """Structured list of specific with all the requirement by category.

    This list of maps have the following structure:

        [
            {
                "id": "18a1d349-e432-4ca9-9617-81bb005d26bc",
                "category": "Room 47",
                "min_number_assets": 15,
                "description": "Shoot the television and the bed",
                "tags": ["room", "luxury", "double"]
            },
            {
                "id": "33261769-20e6-4ec6-b793-d1147de98a90",
                "category": "Bathroom 47",
                "min_number_assets": 15,
                "description": "",
                "tags": ["bathroom"]
            },
            {
                "id": "48401f9a-a243-4606-a29c-cb1514fae722",
                "category": "Room 32",
                "min_number_assets": 15,
                "description": "Shoot the ceiling",
                "tags": ["room", "standard", "single"]
            },
        ]
    """

    @orm.validates('requirement_items')
    def validate_requirement_items(self, key: str, values: t.Sequence) -> t.Sequence:
        """Validate if requirement_items payload is in the correct format.

        :param key: Attribute name.
        :param values: Requirement items payload.
        :return: Validated payload.
        """
        request = self.request
        user_id = str(request.user.id) if request else None
        current_value = list(self.requirement_items) if self.requirement_items else []
        if values:
            for item in values:
                if not item.get('created_by') and user_id:
                    item['created_by'] = user_id
                if not item.get('created_at'):
                    item['created_at'] = datetime_utcnow().isoformat()

        if values or current_value:
            requirements_schema = RequirementItems()
            try:
                values = requirements_schema.deserialize(values)
            except colander.Invalid as exc:
                raise ValidationError(message='Invalid payload for requirement_items', name=key)

        return values

    number_required_assets = sa.Column(
        'number_required_assets',
        sa.Integer(),
        default=10
    )
    """Number of required assets of an Order."""

    @orm.validates('number_required_assets')
    def validate_number_required_assets(self, key: str, value: int) -> int:
        """Validate number_required_assets checking if the order is using requirement_items.

        :param key: Attribute name.
        :param value: Number of required assets value.
        :return: Number of required after validation.
        """
        if value and self.requirement_items:
            logger.warn('Number of required assets will not be set when using requirement items.')

        if self.requirement_items:
            value = 0
            for item in self.requirement_items:
                value += item.get('min_number_assets')

        return value

    requirements = sa.Column(
        'requirements',
        sa.Text,
        default=''
    )
    """Human-readable requirements for an Order."""

    @orm.validates('requirements')
    def validate_requirements(self, key: str, value: str) -> str:
        """Validate requirements checking if the order is using requirement_items.

        :param key: Attribute name.
        :param value: Requirements value.
        :return: Requirements after validation.
        """
        if value or self.requirement_items:
            logger.warn('Requirements will not be set when using requirement items.')

        if self.requirement_items:
            value = ''
            for item in self.requirement_items:
                category = item.get('category')
                description = item.get('description')
                min_number_assets = item.get('min_number_assets')
                value += f'Category: {category}: {min_number_assets}\n' \
                         f'Description: {description}\n\n'

        return value

    actual_order_price = sa.Column(
        'actual_order_price',
        sa.Integer,
        nullable=True,
        default=default_actual_order_price,
        info={
            'colanderalchemy': {
                'title': 'Actual Order Price',
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

    additional_charges = sa.Column(
        JSONB,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Additional Charges',
                'typ': colander.List,
                'missing': None,
            }
        }
    )
    """Additional charges to be applied to this Order."""

    @orm.validates('additional_charges')
    def validate_additional_charges(self, key: str, value: t.Sequence) -> t.Sequence:
        """Validate if additional_charges payload is in the correct format.

        :param key: Attribute name.
        :param value: Additional charges payload.
        :return: Validated payload
        """
        current_value = list(self.additional_charges) if self.additional_charges else []
        if value or current_value:
            charges_schema = OrderCharges()
            try:
                new_value = charges_schema.deserialize(value)
            except colander.Invalid as e:
                raise ValidationError(message='Invalid payload for additional_charges', name=key)

            value = order_charges_update(current_value, new_value)

            # Force total_order_price recalculation
            flag_modified(self, 'actual_order_price')
            flag_modified(self, 'additional_charges')
        return value

    @property
    def total_additional_charges(self) -> int:
        """Return the total of additional charges."""
        total = 0
        additional_charges = self.additional_charges
        if additional_charges:
            for charge in additional_charges:
                total += charge['amount']
        return total

    total_order_price = sa.Column(
        sa.Integer,
        nullable=True,
        default=default_actual_order_price,
        info={
            'colanderalchemy': {
                'title': 'Total Order Price',
                'missing': None,
                'typ': colander.Integer
            }
        }
    )
    """Total price to be paid, by the customer, for this order.

    Total amount to be paid by the customer for this order.
    This value is a sum of actual_order_price and all additional_charges for this Order.

    This value is expressed in cents.
    """

    # Calculate total_order_price
    @sautils.observes('actual_order_price')
    def _calculate_total_order_price(self, actual_order_price: int):
        """Calculate the total order price.

        :param actual_order_price: Order price to be charged to the customer.
        """
        actual_order_price = actual_order_price if actual_order_price else 0
        total_additional_charges = self.total_additional_charges
        self.total_order_price = actual_order_price + total_additional_charges

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
        foreign_keys='Assignment.order_id',
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
        JSONB,
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
        JSONB,
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

    tech_requirements = association_proxy('project', 'tech_requirements')
    """Project tech requirements."""

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

    @sautils.observes('project_id')
    def _project_id_observer(self, project_id):
        """Update path when project id changes."""
        if project_id:
            project = Item.get(project_id)
            self.path = project.path + [self.id]

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

    def update(self, values: dict):
        """Custom update method to handle special case.

        :param values: Dictionary containing attributes and values
        :type values: dict
        """
        if 'requirement_items' in values:
            # force update requirement items before all other fields
            self.requirement_items = values.pop('requirement_items')
        super().update(values)

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
        return data

    @cache_region.cache_on_arguments(should_cache_fn=enable_cache)
    def to_dict(self, excludes: list=None, includes: list=None):
        """Return a dict representation of this object."""
        data = super().to_dict(excludes=excludes, includes=includes)
        data['assignments'] = []
        for assignment in self.assignments:
            assignment_data = assignment.to_summary_dict()
            assignment_data = assignment._apply_actors_info(assignment_data)
            data['assignments'].append(assignment_data)

        if data['assignments']:
            data['assignment'] = data['assignments'][-1]

        data['briefing'] = self.project.briefing
        data['scheduled_datetime'] = self.deliver_date

        # add_user_info_to_state_history(self.state_history)
        if includes and 'state_history' in includes:
            # Workflow history
            add_user_info_to_state_history(self.state_history)

        # HACK: An issue with cache prevents us from adding a specialized to_dict on LeadOrder
        # so, the quick solution is to check subtype here.
        if self.type == 'leadorder':
            data['confirmation_fields'] = self.confirmation_fields or []

        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data


@event.listens_for(Order, 'after_update')
def order_after_update(mapper, connection, target):
    """Invalidate Order cache after instance update."""
    cache_manager.refresh(target)
    for assignment in target.assignments:
        cache_manager.refresh(assignment)
