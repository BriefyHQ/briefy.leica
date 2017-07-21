"""Views to handle Orders creation."""
from briefy.common.db import datetime_utcnow
from briefy.leica.config import LATE_SUBMISSION_SECONDS
from briefy.leica.events import order as events
from briefy.leica.models import Assignment
from briefy.leica.models import LeadOrder
from briefy.leica.models import Order
from briefy.leica.models import Project
from briefy.ws import CORS_POLICY
from briefy.ws.resources import HistoryService
from briefy.ws.resources import RESTService
from briefy.ws.resources import VersionsService
from briefy.ws.resources import WorkflowAwareResource
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from cornice.resource import view
from datetime import timedelta
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import Allow
from sqlalchemy import and_
from sqlalchemy import or_


COLLECTION_PATH = '/orders'
PATH = COLLECTION_PATH + '/{id}'


class OrderFactory(BaseFactory):
    """Order context factory."""

    model = Order

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:customers', ['create', 'list', 'view', 'edit'])
        ]
        return _acls


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=OrderFactory)
class OrderService(RESTService):
    """Orders service."""

    model = Order
    default_order_by = 'created_at'
    filter_related_fields = [
        'project.title', 'project.id', 'project.status', '_location.locality',
        '_location.country', '_location.fullname', '_location.formatted_address',
        'customer.title', 'assignment.id'
    ]

    _default_notify_events = {
        'POST': events.OrderCreatedEvent,
        'PUT': events.OrderUpdatedEvent,
        'GET': events.OrderLoadedEvent,
        'DELETE': events.OrderDeletedEvent,
    }

    @view(validators='_run_validators', permission='create')
    def collection_post(self, model=None):
        """Add a new instance of LeadOrder or Order depending of Project.order_type.

        :returns: Newly created instance of model Order or LeadOrder.
        """
        request = self.request
        user = request.user
        user_groups = user.groups
        payload = request.validated
        payload['source'] = 'customer' if 'g:customers' in user_groups else 'briefy'
        project = Project.get(payload.get('project_id'))
        add_order_roles = project.add_order_roles

        if project.order_type.value == 'leadorder':
            model = LeadOrder
        else:
            model = model if model else Order

        if len(set(add_order_roles) & set(user_groups)) == 0:
            model_name = 'lead' if model == LeadOrder else 'order'
            raise HTTPForbidden(f'You are not allowed to add a new {model_name} to this project')

        request.validated = payload
        return super().collection_post(model=model)

    @property
    def filter_allowed_fields(self) -> list:
        """List of fields allowed in filtering and sorting.

        For Orders/LeadOrders, we add support to filter by type.

        :returns: List of field names supported in filtering and sorting.
        """
        allowed_filters = super().filter_allowed_fields
        allowed_filters.append('type')
        return allowed_filters

    def default_filters(self, query) -> object:
        """Default filters to be applied to every query.

        This is supposed to be specialized by resource classes.
        :returns: A tuple of default filters to be applied to queries.
        """
        user = self.request.user
        model = self.model
        custom_filter = self.request.params.get('_custom_filter')
        if 'g:customers' in user.groups and custom_filter == 'customer_deliveries':
            query = query.filter(
                or_(
                    and_(
                        model.state.in_(('accepted', 'refused', 'in_qa')),
                        model.accept_date.isnot(None)
                    ),
                    model.state == 'delivered'
                )
            )
        elif custom_filter == 'late_first_submission':
            config_delta = timedelta(seconds=int(LATE_SUBMISSION_SECONDS))
            date_limit = datetime_utcnow() - config_delta
            query = query.filter(
                model.assignments.any(
                    and_(
                        Assignment.state == 'awaiting_assets',
                        Assignment.scheduled_datetime <= date_limit,
                        Assignment.last_approval_date.is_(None),
                    )
                )
            )
        elif custom_filter == 'late_re_submission':
            config_delta = timedelta(seconds=int(LATE_SUBMISSION_SECONDS))
            date_limit = datetime_utcnow() - config_delta
            query = query.filter(
                model.assignments.any(
                    and_(
                        Assignment.state == 'awaiting_assets',
                        Assignment.last_approval_date <= date_limit,
                        Assignment.submission_path.isnot(None)
                    )
                )
            )
        return query


@resource(
    collection_path=PATH + '/transitions',
    path=PATH + '/transitions/{transition_id}',
    cors_policy=CORS_POLICY,
    factory=OrderFactory
)
class OrderWorkflowService(WorkflowAwareResource):
    """Order workflow resource."""

    model = Order


@resource(
    collection_path=PATH + '/versions',
    path=PATH + '/versions/{version_id}',
    cors_policy=CORS_POLICY,
    factory=OrderFactory
)
class OrderVersionsService(VersionsService):
    """Versioning of Orders."""

    model = Order


@resource(
    collection_path=PATH + '/history',
    path=PATH + '/history/{item_id}',
    cors_policy=CORS_POLICY,
    factory=OrderFactory
)
class OrderHistory(HistoryService):
    """Workflow history of Orders."""

    model = Order
