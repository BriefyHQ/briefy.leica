"""Views to handle Finance Dashboards."""
from briefy.leica.models.dashboard.finance import DashboardFinanceOrder
from briefy.leica.views.dashboard import ORDER_PROJECT_COLS
from briefy.ws import CORS_POLICY
from briefy.ws.resources import SQLQueryService
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
class DashboardFinanceOrderService(SQLQueryService):
    """Dashboard Finance: Order Service."""

    _columns_map = ORDER_PROJECT_COLS

    _collection_query = """
    SELECT
    count(active_orders.id) as total,
    active_orders.title,
    active_orders.project_id,

    sum(
    CASE WHEN
    active_orders.state = 'received'
    THEN 1 ELSE 0
    END) as received,

    sum(
    CASE WHEN
    active_orders.state = 'assigned'
    THEN 1 ELSE 0
    END) as assigned,

    sum(
    CASE WHEN
    active_orders.state = 'scheduled'
    THEN 1 ELSE 0
    END) as scheduled,

    sum(
    CASE WHEN
    active_orders.state IN ('in_qa', 'refused')
    THEN 1 ELSE 0
    END) as in_qa,

    sum(
    CASE WHEN active_orders.state = 'cancelled'
    THEN 1 ELSE 0
    END) as cancelled,

    sum(
    CASE WHEN active_orders.state IN ('delivered', 'accepted')
    THEN 1 ELSE 0
    END) as completed

    FROM

    (SELECT DISTINCT orders.id, orders.project_id, projects.title, orders.state FROM

    (SELECT i.id, i.state, i.title, o.project_id
    FROM items as i JOIN orders as o on i.id = o.id
    WHERE i.type = '{type}' AND
    i.state IN ('received', 'assigned', 'scheduled', 'cancelled',
    'delivered', 'accepted', 'in_qa', 'refused')
    ) as orders JOIN

    (SELECT i.id, i.state, i.title
    FROM items as i JOIN projects as p on i.id = p.id
    WHERE i.state = 'ongoing') as projects
    on orders.project_id = projects.id

    ) as active_orders GROUP BY
    active_orders.title,
    active_orders.project_id
    ORDER BY active_orders.title
    """

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
