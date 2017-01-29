"""Views to handle Pm Dashboards."""
from briefy.leica.models.dashboard.pm import DashboardPMOrder
from briefy.leica.views.dashboard import ORDER_PROJECT_COLS
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


class DashboardPmFactory(BaseFactory):
    """Dashboard Pm context factory."""

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
