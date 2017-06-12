"""Views to handle Customer Dashboards."""
from briefy.leica.models.dashboard.customer import DashboardCustomerAllLeads
from briefy.leica.models.dashboard.customer import DashboardCustomerAllOrders
from briefy.leica.models.dashboard.customer import DashboardCustomerDeliveredOrders
from briefy.leica.views.dashboard import DELIVERED_ORDERS_COLS
from briefy.leica.views.dashboard import LEAD_PROJECT_COLS
from briefy.leica.views.dashboard import ORDER_PROJECT_COLS
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

    _columns_map = ORDER_PROJECT_COLS

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


class DashboardCustomerAllLeadsFactory(BaseFactory):
    """Dashboard Customer: All Leads context factory."""

    model = DashboardCustomerAllOrders

    __base_acl__ = [
        (Allow, 'g:customers', ['list', 'view']),
    ]


COLLECTION_PATH = '/dashboards/customer/lead'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardCustomerAllLeadsFactory)
class DashboardCustomerAllLeadsService(RESTService):
    """Dashboard Customer: All Leads Service."""

    model = DashboardCustomerAllLeads
    friendly_name = model.__name__
    default_order_by = 'title'

    _columns_map = LEAD_PROJECT_COLS

    def default_filters(self, query) -> object:
        """Default filters to be applied to every query.

        This is supposed to be specialized by resource classes.
        :returns: A tuple of default filters to be applied to queries.
        """
        user = self.request.user
        query = query.params(user_id_1=user.id)
        return query
