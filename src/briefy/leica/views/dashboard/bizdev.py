"""Views to handle BizDev Dashboards."""
from briefy.leica.models.dashboard.bizdev import DashboardBizDevOrder
from briefy.leica.views.dashboard import DASHBOARD_ALL_ORDERS_CUSTOMER_QUERY
from briefy.leica.views.dashboard import ORDER_PROJECT_COLS
from briefy.ws import CORS_POLICY
from briefy.ws.resources import SQLQueryService
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
class DashboardBizDevOrderService(SQLQueryService):
    """Dashboard BizDev: Order Service."""

    model = DashboardBizDevOrder
    default_order_by = 'title'

    _columns_map = ORDER_PROJECT_COLS

    _collection_query = DASHBOARD_ALL_ORDERS_CUSTOMER_QUERY

    def query_params(self, query: str) -> str:
        """Apply query parameters based on request.

        This is supposed to be specialized by resource classes.

        :query: string with a query to be parametrized
        :returns: string with a query after adding parameters
        """
        principal_id = self.request.user.id
        return query.format(principal_id=principal_id, type='order')

    def transform(self, data: list) -> list:
        """Transform data items after query execution.

        :data: list of records to be transformed
        :returns: list of records after transformation
        """
        for item in data:
            project_id = item.pop('project_id')
            item['absolute_url'] = f'/projects/{project_id}'
        return data
