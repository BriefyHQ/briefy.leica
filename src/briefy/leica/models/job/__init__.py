"""Briefy Leica Assignment model."""
from briefy.common.db.types import AwareDateTime
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica.cache import cache_manager
from briefy.leica.cache import cache_region
from briefy.leica.cache import enable_cache
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.job import workflows
from briefy.leica.models.job.order import Order
from briefy.leica.utils.transitions import get_transition_date_from_history
from briefy.leica.utils.user import add_user_info_to_state_history
from briefy.leica.vocabularies import TypesOfSetChoices
from datetime import datetime
from sqlalchemy import event
from sqlalchemy import orm
from sqlalchemy import select
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import TimezoneType
from zope.interface import implementer
from zope.interface import Interface

import colander
import copy
import sqlalchemy as sa
import sqlalchemy_utils as sautils


__summary_attributes__ = [
    'id', 'title', 'description', 'slug', 'created_at', 'updated_at', 'state',
    'number_required_assets', 'approvable', 'total_assets', 'total_approvable_assets',
    'category', 'scheduled_datetime', 'professional', 'timezone', 'professional_user',
    'payout_value', 'payout_currency', 'travel_expenses', 'submission_path'
]

__listing_attributes__ = __summary_attributes__ + [
    'assignment_date', 'last_approval_date', 'submission_date', 'last_submission_date',
    'set_type', 'number_required_assets', 'category', 'availability', 'additional_compensation',
    'reason_additional_compensation', 'qa_manager', 'state_history', 'requirements', 'pool_id',
    'location', 'project', 'closed_on_date', 'pool', 'delivery', 'refused_times'
]

__colander_alchemy_config_overrides__ = \
    copy.copy(mixins.AssignmentBriefyRoles.__colanderalchemy_config__['overrides'])

__colander_alchemy_config_overrides__.update(
    dict(
        customer_message={
            'title': 'Customer message',
            'default': '',
            'missing': colander.drop,
            'typ': colander.String()
        },
        additional_message={
            'title': 'Transition Additional Message',
            'default': '',
            'missing': colander.drop,
            'typ': colander.String()
        },
    )
)


def create_slug_from_order(context):
    """Create a slug for Assignment from the Order slug."""
    order_id = context.current_parameters.get('order_id')
    order = Order.get(order_id)
    total = len(order.assignments) + 1
    return '{slug}_{total:02d}'.format(slug=order.slug, total=total)


class IAssignment(Interface):
    """Marker interface for an Assignment."""


class AssignmentDates:
    """Mixin providing date-related information of an Assignment."""

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

    assignment_date = sa.Column(
        AwareDateTime(),
        nullable=True,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Last assignment date for this assignment',
                'missing': colander.drop,
                'typ': colander.DateTime
            }
        }
    )
    """Last assignment date for this assignment."""

    last_approval_date = sa.Column(
        AwareDateTime(),
        nullable=True,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Last QA transition date for this assignment',
                'missing': colander.drop,
                'typ': colander.DateTime
            }
        }
    )
    """Last QA transition date for this assignment."""

    submission_date = sa.Column(
        AwareDateTime(),
        nullable=True,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'First submission date.',
                'missing': colander.drop,
                'typ': colander.DateTime
            }
        }
    )
    """First submission date."""

    last_submission_date = sa.Column(
        AwareDateTime(),
        nullable=True,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Last submission date.',
                'missing': colander.drop,
                'typ': colander.DateTime
            }
        }
    )
    """Last submission date date for this Assignment."""


@implementer(IAssignment)
class Assignment(AssignmentDates, mixins.AssignmentBriefyRoles,
                 mixins.AssignmentFinancialInfo, mixins.LeicaMixin,
                 mixins.VersionMixin, Base):
    """An Assignment within an Order."""

    _workflow = workflows.AssignmentWorkflow

    __summary_attributes__ = __summary_attributes__
    __summary_attributes_relations__ = [
        'project', 'comments', 'location', 'professional', 'customer',
        'pool', 'external_id', 'active_order'
    ]
    __listing_attributes__ = __listing_attributes__

    __raw_acl__ = (
        ('create', ('g:briefy_pm', 'g:briefy_finance', 'g:briefy_scout', 'g:system')),
        ('list', ('g:briefy_qa', 'g:briefy_scout', 'g:briefy_finance', 'g:system')),
        ('view', ('g:briefy_qa', 'g:briefy_scout', 'g:briefy_finance', 'g:system')),
        ('edit', ('g:briefy_pm', 'g:briefy_finance', 'g:briefy_scout', 'g:system')),
        ('delete', ('g:briefy_finance', 'g:system')),
    )

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'order', 'comments',
            'professional', 'assets', 'project', 'location',
            '_scout_manager', '_project_manager', '_qa_manager',
            '_professional_user', 'pool', 'active_order'
        ],
        'overrides': __colander_alchemy_config_overrides__
    }

    __versioned__ = {
        'exclude': ['state_history', '_state_history', 'timezone']
    }
    """SQLAlchemy Continuum settings.

    By default we do not keep track of state_history and helper columns.
    """

    _slug = sa.Column('slug',
                      sa.String(255),
                      nullable=True,
                      index=True,
                      default=create_slug_from_order,
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

    refused_times = sa.Column(
        sa.Integer(),
        default=0
    )
    """Number times the Assignment was refused."""

    set_type = sa.Column(
        sautils.ChoiceType(TypesOfSetChoices, impl=sa.String()),
        nullable=True,
        default='new',
        info={
            'colanderalchemy': {
                'title': 'Type of Set',
                'default': colander.null,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Type of Set when in QA.

    Define the type of set when in QA. It will be updated by the workflow.
    """

    order_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('orders.id'),
        index=True,
        nullable=False,
        info={
            'colanderalchemy': {
                'title': 'Order ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
    )
    """Order ID.

    Relantionship to :class:`briefy.leica.models.job.order.Order`
    """

    pool_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('pools.id'),
        index=True,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Pool ID',
                'validator': colander.uuid,
                'typ': colander.String,
                'missing': colander.drop,
            }
        }
    )
    """Pool ID.

    Relationship to :class:`briefy.leica.models.job.pool.Pool`
    """

    # Professional
    professional_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('professionals.id'),
        index=True,
        nullable=True,
        info={'colanderalchemy': {
            'title': 'Professional ID',
            'validator': colander.uuid,
            'missing': colander.drop,
            'typ': colander.String}}
    )
    """Professional ID.

    Relationship with :class:`briefy.leica.models.professional.Professional`.

    Professional ID linked with this Assignment.
    """

    professional = orm.relationship(
        'Professional',
    )
    """Relationship with :class:`briefy.leica.models.professional.Professional`.

    Professional instance linked with this Assignment.
    """

    # Assets for this Assignment
    assets = orm.relationship(
        'Asset',
        backref=orm.backref('assignment'),
        lazy='dynamic'
    )
    """Assets connected to this Assignment.

    Collection of :class:`briefy.leica.models.asset.Asset`.
    """

    approvable_assets = orm.relationship(
        'Asset',
        primaryjoin='''and_(
            Asset.assignment_id == Assignment.id,
            Asset.state.in_(('approved', 'pending', 'delivered'))
        )''',
        viewonly=True

    )
    """Approvable assets connected to this Assignment.

    To be listed here, an Asset, needs to be on one of the following states:

        * approved

        * pending

        * delivered

    Collection of :class:`briefy.leica.models.asset.Asset`.
    """

    comments = orm.relationship(
        'Comment',
        foreign_keys='Comment.entity_id',
        order_by='desc(Comment.created_at)',
        primaryjoin='Comment.entity_id == Assignment.id',
        lazy='dynamic'
    )
    """Comments connected to this Assignment.

    Collection of :class:`briefy.leica.models.comment.Comment`.
    """

    submission_path = sa.Column(
        sautils.URLType,
        nullable=True,
        default=None,
        info={
            'colanderalchemy': {
                'title': 'Path to photographer submission',
                'validator': colander.url,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Path to the assets submission.

    On Knack it usually pointed to a google-drive folder where
    the Professional have write-permission.
    This will be deprecated when assets upload is handled also using Leica.
    """

    project = orm.relationship(
        'Project',
        secondary='join(Order, Project, Order.project_id == Project.id)',
        secondaryjoin='Order.project_id == Project.id',
        primaryjoin='Order.id == Assignment.order_id',
        viewonly=True,
        uselist=False
    )
    """Project related to this Assignment.

    Instance of :class:`briefy.leica.models.project.Project`.
    """

    location = orm.relationship(
        'OrderLocation',
        secondary='orders',
        secondaryjoin='Order.id == OrderLocation.order_id',
        primaryjoin='Order.id == Assignment.order_id',
        backref=orm.backref('assignments'),
        viewonly=True,
        uselist=False
    )
    """OrderLocations related to this Assignment.

    Instance of :class:`briefy.leica.models.job.location.OrderLocation`.
    """

    release_contract = sa.Column(
        sautils.URLType,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Release Contract',
                'validator': colander.url,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )

    timezone = sa.Column(TimezoneType(backend='pytz'), default='UTC')
    """Timezone in which this address is located.

    i.e.: UTC, Europe/Berlin
    Important: this will be updated by the Order timezone observer.
    """

    @sautils.aggregated('assets', sa.Column(sa.Integer, default=0))
    def total_assets(self):
        """Total number of assets.

        Counter of the number of assets in this Assignment.
        """
        return sa.func.count('1')

    @sautils.aggregated('approvable_assets', sa.Column(sa.Integer, default=0))
    def total_approvable_assets(self):
        """Total number of assets that can be approved.

        Counter of the number of assets in this Assignment that can be approved.
        """
        return sa.func.count('1')

    @property
    def approvable(self) -> bool:
        """Check if this Assignment could be approved.

        :returns: Boolean indicating if it is possible to approve this Assignment.
        """
        approvable_assets_count = self.total_approvable_assets
        check_images = self.order.number_required_assets <= approvable_assets_count
        return check_images

    @declared_attr
    def title(cls) -> str:
        """Return the title of an Order."""
        return orm.column_property(
            select([Order.title]).where(
                Order.id == cls.order_id
            ),
        )

    @declared_attr
    def delivery(cls) -> str:
        """Return the delivery of an Order."""
        return orm.column_property(
            select([Order._delivery]).where(
                Order.id == cls.order_id
            ),
        )

    @declared_attr
    def description(cls) -> str:
        """Return the description of an Order."""
        return orm.column_property(
            select([Order.description]).where(
                Order.id == cls.order_id
            ),
        )

    @declared_attr
    def customer_order_id(cls) -> str:
        """Return the customer_order_id of an Order."""
        return orm.column_property(
            select([Order.customer_order_id]).where(
                Order.id == cls.order_id
            ),
        )

    @declared_attr
    def order_slug(cls) -> str:
        """Return the order_id (slug) of an Order."""
        return orm.column_property(
            select([Order.slug]).where(
                Order.id == cls.order_id
            ),
        )

    @declared_attr
    def requirements(cls) -> str:
        """Return the requirements of an Order."""
        return orm.column_property(
            select([Order.requirements]).where(
                Order.id == cls.order_id
            ),
        )

    @declared_attr
    def category(cls) -> str:
        """Return the category of an Order."""
        return orm.column_property(
            select([Order.category]).where(
                Order.id == cls.order_id
            ),
        )

    @declared_attr
    def number_required_assets(cls) -> str:
        """Return the number_required_assets of an Order."""
        return orm.column_property(
            select([Order.number_required_assets]).where(
                Order.id == cls.order_id
            ),
        )

    @declared_attr
    def availability(cls) -> list:
        """Return the availability dates of an Order."""
        return orm.column_property(
            select([Order._availability]).where(
                Order.id == cls.order_id
            ),
        )

    customer_approval_date = sa.Column(
        AwareDateTime(),
        nullable=True,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Customer approval date.',
                'missing': colander.drop,
                'typ': colander.DateTime
            }
        }
    )
    """Last Accept/Refusal date for the parent order."""

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

        transitions = ('assign', 'self_assign', 'assign_pool', )
        updated_if_changed('assignment_date', transitions, False)

        transitions = ('approve', 'reject', )
        updated_if_changed('last_approval_date', transitions, False)

        transitions = ('upload', )
        updated_if_changed('submission_date', transitions, True)
        updated_if_changed('last_submission_date', transitions, False)

        transitions = ('approve', 'refuse')
        updated_if_changed('customer_approval_date', transitions, False)

        if keep_updated_at:
            self.updated_at = updated_at

    # Relevant dates
    @sautils.observes('state')
    def dates_observer(self, state) -> datetime:
        """Calculate dates on a change of a state."""
        # Update all dates
        self._update_dates_from_history()

    @property
    def closed_on_date(self) -> datetime:
        """Return the date of the closing info for this assignment."""
        state_history = self.state_history
        transitions = ('approve', 'perm_reject', 'cancel')
        return get_transition_date_from_history(transitions, state_history)

    @property
    def briefing(self) -> str:
        """Return the briefing URL for the parent project."""
        return self.order.project.briefing

    @property
    def assigned(self) -> bool:
        """Return if this Assignment is assigned or not."""
        return True if (self.assignment_date and self.professional_id) else False

    @cache_region.cache_on_arguments(should_cache_fn=enable_cache)
    def to_summary_dict(self) -> dict:
        """Return a summarized version of the dict representation of this Class.

        Used to serialize this object within a parent object serialization.
        :returns: Dictionary with fields and values used by this Class
        """
        data = super().to_summary_dict()
        data['category'] = self.category.value
        data = self._apply_actors_info(data)
        return data

    @cache_region.cache_on_arguments(should_cache_fn=enable_cache)
    def to_listing_dict(self) -> dict:
        """Return a summarized version of the dict representation of this Class.

        Used to serialize this object within a parent object serialization.
        :returns: Dictionary with fields and values used by this Class
        """
        data = super().to_listing_dict()
        data['set_type'] = self.set_type.value
        data['category'] = self.category.value \
            if isinstance(self.category, CategoryChoices) else self.category
        data = self._apply_actors_info(data)
        return data

    @cache_region.cache_on_arguments(should_cache_fn=enable_cache)
    def to_dict(self, excludes: list=None, includes: list=None):
        """Return a dict representation of this object."""
        excludes = list(excludes) if excludes else []
        excludes.extend('approvable_assets')
        data = super().to_dict(excludes=excludes, includes=includes)
        data['title'] = self.title
        data['description'] = self.description
        data['briefing'] = self.briefing
        data['assignment_date'] = self.assignment_date
        data['last_approval_date'] = self.last_approval_date
        data['last_submission_date'] = self.last_submission_date
        data['closed_on_date'] = self.closed_on_date
        data['category'] = self.category.value \
            if isinstance(self.category, CategoryChoices) else self.category
        data['slug'] = self.slug
        data['set_type'] = self.set_type.value \
            if isinstance(self.set_type, TypesOfSetChoices) else self.set_type
        data['timezone'] = self.timezone
        data['tech_requirements'] = self.order.tech_requirements
        data['availability'] = self.availability
        data['category'] = self.category.value
        data['order'] = self.order.to_summary_dict() if self.order else None
        data['location'] = self.location.to_summary_dict() if self.location else None
        if data['project']:
            # Project delivery data used on the 'approve' transition
            # to deliver assets. (copying over and renaming - takes place
            # on ms.laure)
            data['project']['delivery'] = self.project.delivery

        # Workflow history
        add_user_info_to_state_history(self.state_history)

        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data


@event.listens_for(Assignment, 'after_update')
def assignment_after_update(mapper, connection, target):
    """Invalidate Assignment cache after instance update."""
    cache_manager.refresh(target)
    cache_manager.refresh(target.order)
