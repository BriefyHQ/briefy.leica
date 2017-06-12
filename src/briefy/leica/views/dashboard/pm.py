"""Views to handle Pm Dashboards."""
from briefy.leica.models.dashboard.pm import DashboardPMAllLeads
from briefy.leica.models.dashboard.pm import DashboardPMDeliveredOrders
from briefy.leica.models.dashboard.pm import DashboardPMOrder
from briefy.leica.views.dashboard import DELIVERED_ORDERS_COLS
from briefy.leica.views.dashboard import LEAD_PROJECT_COLS
from briefy.leica.views.dashboard import ORDER_PROJECT_COLS
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


class DashboardPmFactory(BaseFactory):
    """Dashboard PM: All Orders context factory."""

    model = DashboardPMOrder

    __base_acl__ = [
        (Allow, 'g:briefy_pm', ['list', 'view']),
    ]


COLLECTION_PATH = '/dashboards/pm/order'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardPmFactory)
class DashboardPmOrderService(RESTService):
    """Dashboard Pm: Order Service."""

    model = DashboardPMOrder
    friendly_name = model.__name__
    default_order_by = 'title'

    _columns_map = ORDER_PROJECT_COLS

    def default_filters(self, query) -> object:
        """Default filters to be applied to every query.

        This is supposed to be specialized by resource classes.
        :returns: A tuple of default filters to be applied to queries.
        """
        user = self.request.user
        query = query.params(user_id_1=user.id, user_id_2=user.id)
        return query


class DashboardPmDeliveredFactory(BaseFactory):
    """Dashboard PM: Delivered Orders context factory."""

    model = DashboardPMDeliveredOrders

    __base_acl__ = [
        (Allow, 'g:briefy_pm', ['list', 'view']),
    ]


COLLECTION_PATH = '/dashboards/pm/delivered'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardPmDeliveredFactory)
class DashboardPMDeliveredOrdersService(RESTService):
    """Dashboard PM: Delivered Orders Service."""

    model = DashboardPMDeliveredOrders
    friendly_name = model.__name__
    default_order_by = 'title'

    _columns_map = DELIVERED_ORDERS_COLS

    def default_filters(self, query) -> object:
        """Default filters to be applied to every query.

        This is supposed to be specialized by resource classes.
        :returns: A tuple of default filters to be applied to queries.
        """
        user = self.request.user
        query = query.params(user_id_1=user.id, user_id_2=user.id)
        return query


class DashboardPMAllLeadsFactory(BaseFactory):
    """Dashboard Customer: All Leads context factory."""

    model = DashboardPMAllLeads

    __base_acl__ = [
        (Allow, 'g:briefy_pm', ['list', 'view']),
    ]


COLLECTION_PATH = '/dashboards/pm/lead'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardPMAllLeadsFactory)
class DashboardPMAllLeadsService(RESTService):
    """Dashboard PM: All Leads Service."""

    model = DashboardPMAllLeads
    friendly_name = model.__name__
    default_order_by = 'title'

    _columns_map = LEAD_PROJECT_COLS

    def default_filters(self, query) -> object:
        """Default filters to be applied to every query.

        This is supposed to be specialized by resource classes.
        :returns: A tuple of default filters to be applied to queries.
        """
        user = self.request.user
        query = query.params(user_id_1=user.id, user_id_2=user.id)
        return query
