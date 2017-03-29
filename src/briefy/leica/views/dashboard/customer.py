"""Views to handle Customer Dashboards."""
from briefy.leica.models.dashboard.customer import DashboardCustomerAllOrders
from briefy.leica.models.dashboard.customer import DashboardCustomerDeliveredOrders
from briefy.leica.views.dashboard import DELIVERED_ORDERS_COLS
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


class DashboardCustomerAllOrdersFactory(BaseFactory):
    """Dashboard Customer: All Orders context factory."""

    model = DashboardCustomerAllOrders

    __base_acl__ = [
        (Allow, 'g:customers', ['list', 'view']),
    ]


COLLECTION_PATH = '/dashboards/customer/order'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardCustomerAllOrdersFactory)
class DashboardCustomerAllOrdersService(RESTService):
    """Dashboard Customer: All Orders Service."""

    model = DashboardCustomerAllOrders
    friendly_name = model.__name__
    default_order_by = 'title'

    _columns_map = (
        {
            'field': 'absolute_url', 'label': 'url',
            'type': 'hidden', 'url': '', 'filter': ''
        },
        {
            'field': 'title', 'label': 'Project',
            'type': 'text', 'url': 'absolute_url', 'filter': ''
        },
        {
            'field': 'total', 'label': 'All Orders',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'received', 'label': 'New Orders',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'assigned', 'label': 'Assigned Orders',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'scheduled', 'label': 'Scheduled Orders',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'in_qa', 'label': 'Orders in QA process',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'cancelled', 'label': 'Cancelled Orders',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'completed', 'label': 'Completed Orders',
            'type': 'integer', 'url': '', 'filter': ''
        }
    )

    def default_filters(self, query) -> object:
        """Default filters to be applied to every query.

        This is supposed to be specialized by resource classes.
        :returns: A tuple of default filters to be applied to queries.
        """
        user = self.request.user
        query = query.params(user_id_1=user.id)
        return query


class DashboardCustomerDeliveredOrdersFactory(BaseFactory):
    """Dashboard Customer: Delivered Orders context factory."""

    model = DashboardCustomerDeliveredOrders

    __base_acl__ = [
        (Allow, 'g:customers', ['list', 'view']),
    ]


COLLECTION_PATH = '/dashboards/customer/delivered'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardCustomerAllOrdersFactory)
class DashboardCustomerDeliveredOrderService(RESTService):
    """Dashboard Customer: Delivered Orders Service."""

    model = DashboardCustomerDeliveredOrders
    friendly_name = model.__name__
    default_order_by = 'title'

    _columns_map = DELIVERED_ORDERS_COLS

    def default_filters(self, query) -> object:
        """Default filters to be applied to every query.

        This is supposed to be specialized by resource classes.
        :returns: A tuple of default filters to be applied to queries.
        """
        user = self.request.user
        query = query.params(user_id_1=user.id)
        return query
