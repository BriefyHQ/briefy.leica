"""Views to handle BizDev Dashboards."""
from briefy.leica.models.dashboard.bizdev import DashboardBizDevOrder
from briefy.leica.views.dashboard import ORDER_PROJECT_COLS
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


class DashboardBizDevFactory(BaseFactory):
    """Dashboard BizDev context factory."""

    model = DashboardBizDevOrder

    __base_acl__ = [
        (Allow, 'g:briefy_bizdev', ['list', 'view']),
    ]


COLLECTION_PATH = '/dashboards/bizdev/order'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardBizDevFactory)
class DashboardBizDevOrderService(RESTService):
    """Dashboard BizDev: Order Service."""

    model = DashboardBizDevOrder
    default_order_by = 'title'

    _columns_map = ORDER_PROJECT_COLS

    def default_filters(self, query) -> object:
        """Default filters to be applied to every query.

        This is supposed to be specialized by resource classes.
        :returns: A tuple of default filters to be applied to queries.
        """
        user = self.request.user
        query = query.params(principal_id_1=user.id, principal_id_2=user.id)
        return query
