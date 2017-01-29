"""Views to handle Finance Dashboards."""
from briefy.leica.models.dashboard.finance import DashboardFinanceOrder
from briefy.leica.views.dashboard import ORDER_PROJECT_COLS
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


class DashboardFinanceFactory(BaseFactory):
    """Dashboard Finance context factory."""

    model = DashboardFinanceOrder

    __base_acl__ = [
        (Allow, 'g:briefy_finance', ['list', 'view']),
    ]


COLLECTION_PATH = '/dashboards/finance/order'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardFinanceFactory)
class DashboardFinanceOrderService(RESTService):
    """Dashboard Finance: Order Service."""

    model = DashboardFinanceOrder
    friendly_name = model.__name__
    default_order_by = 'title'

    _columns_map = ORDER_PROJECT_COLS
