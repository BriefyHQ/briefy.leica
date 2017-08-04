"""Views to handle Pm Dashboards."""
from briefy.leica.models.dashboard.pm import DashboardPMAllLeads
from briefy.leica.models.dashboard.pm import DashboardPMDeliveredOrders
from briefy.leica.models.dashboard.pm import DashboardPMOrder
from briefy.leica.views.dashboard import DELIVERED_ORDERS_COLS
from briefy.leica.views.dashboard import LEAD_PROJECT_COLS
from briefy.leica.views.dashboard import ORDER_PROJECT_COLS
from briefy.ws import CORS_POLICY
from briefy.ws.resources import SQLQueryService
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
class DashboardPmOrderService(SQLQueryService):
    """Dashboard Pm: Order Service."""

    model = DashboardPMOrder
    default_order_by = 'title'

    _columns_map = ORDER_PROJECT_COLS

    _collection_query = '''
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
    active_orders.state = 'in_qa'
    AND active_orders.accept_date IS NULL
    THEN 1 ELSE 0
    END) as in_qa,

    sum(
    CASE WHEN active_orders.state = 'cancelled'
    THEN 1 ELSE 0
    END) as cancelled,

    sum(
    CASE WHEN
        active_orders.state = 'delivered'
        OR
        active_orders.state IN ('accepted', 'refused', 'perm_refused', 'in_qa')
        AND
        active_orders.accept_date IS NOT NULL
    THEN 1 ELSE 0
    END) as delivered

    FROM

    (SELECT DISTINCT orders.id, orders.project_id,
    projects.title, orders.state, orders.accept_date FROM

    (SELECT i.id, i.state, i.title, o.accept_date, o.project_id
    FROM items as i JOIN orders as o on i.id = o.id
    WHERE i.type = '{type}' AND
    i.state IN ('received', 'assigned', 'scheduled', 'cancelled',
    'delivered', 'accepted', 'in_qa', 'refused', 'perm_refused')
    ) as orders JOIN

    (SELECT i.id, i.state, i.title
    FROM items as i JOIN projects as p on i.id = p.id
    JOIN localroles as l on p.id = l.item_id
    WHERE l.principal_id = '{principal_id}') as projects
    on orders.project_id = projects.id

    ) as active_orders GROUP BY
    active_orders.title,
    active_orders.project_id
    ORDER BY active_orders.title
    '''

    def query_params(self, query: str) -> str:
        """Apply query parameters based on request.

        This is supposed to be specialized by resource classes.

        :query: string with a query to be parametrized
        :returns: string with a query after adding parameters
        """
        principal_id = self.request.user.id
        return query.format(principal_id=principal_id, type='order')

    def transform(self, data: list) -> list:
        """Transform data items after query execution

        :data: list of records to be transformed
        :returns: list of records after transformation
        """
        for item in data:
            project_id = item.pop('project_id')
            item['absolute_url'] = f'/projects/{project_id}'
        return data


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
class DashboardPMDeliveredOrdersService(SQLQueryService):
    """Dashboard PM: Delivered Orders Service."""

    model = DashboardPMDeliveredOrders
    default_order_by = 'title'

    _columns_map = DELIVERED_ORDERS_COLS

    _collection_query = '''
    SELECT
    count(active_orders.id) as total,
    active_orders.title,
    active_orders.project_id,
    sum(
    CASE WHEN
    active_orders.state = 'delivered'
    AND active_orders.accept_date IS NULL
    THEN 1 ELSE 0
    END) as newly_delivered,
    sum(
    CASE WHEN
    active_orders.state IN ('refused', 'in_qa')
    AND active_orders.accept_date IS NOT NULL
    THEN 1 ELSE 0
    END) as further_revision,
    sum(
    CASE WHEN active_orders.state = 'delivered'
    AND active_orders.accept_date IS NOT NULL
    THEN 1 ELSE 0
    END) as re_delivered,
    sum(
    CASE WHEN active_orders.state = 'accepted'
    THEN 1 ELSE 0
    END) as completed
    FROM

    (SELECT DISTINCT orders.id, orders.project_id,
    projects.title, orders.state, orders.accept_date FROM

    (SELECT i.id, i.state, i.title, o.accept_date, o.project_id
    FROM items as i JOIN orders as o on i.id = o.id
    WHERE i.type = '{type}' AND
    i.state IN ('delivered', 'accepted', 'in_qa', 'refused')
    ) as orders JOIN

    (SELECT i.id, i.state, i.title
    FROM items as i JOIN projects as p on i.id = p.id
    JOIN localroles as l on p.id = l.item_id
    WHERE l.principal_id = '{principal_id}') as projects
    on orders.project_id = projects.id

    ) as active_orders GROUP BY
    active_orders.title,
    active_orders.project_id
    ORDER BY active_orders.title
    '''

    def query_params(self, query: str) -> str:
        """Apply query parameters based on request.

        This is supposed to be specialized by resource classes.

        :query: string with a query to be parametrized
        :returns: string with a query after adding parameters
        """
        principal_id = self.request.user.id
        return query.format(principal_id=principal_id, type='order')

    def transform(self, data: list) -> list:
        """Transform data items after query execution

        :data: list of records to be transformed
        :returns: list of records after transformation
        """
        for item in data:
            project_id = item.pop('project_id')
            item['absolute_url'] = f'/projects/{project_id}'
        return data


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
class DashboardPMAllLeadsService(SQLQueryService):
    """Dashboard PM: All Leads Service."""

    model = DashboardPMAllLeads
    default_order_by = 'title'

    _columns_map = LEAD_PROJECT_COLS

    _collection_query = '''
    SELECT
    count(active_orders.id) as total,
    active_orders.title,
    active_orders.project_id,

    sum(
    CASE WHEN
    active_orders.state = 'new'
    THEN 1 ELSE 0
    END) as open,

    sum(
    CASE WHEN active_orders.state = 'cancelled'
    THEN 1 ELSE 0
    END) as cancelled,

    sum(
    CASE WHEN active_orders.state NOT IN ('new', 'cancelled')
    THEN 1 ELSE 0
    END) as confirmed

    FROM

    (SELECT DISTINCT orders.id, orders.project_id,
    projects.title, orders.state, orders.accept_date FROM

    (SELECT i.id, i.state, i.title, o.accept_date, o.project_id
    FROM items as i JOIN orders as o on i.id = o.id
    WHERE i.type = '{type}' AND
    i.state IN ('new', 'received', 'assigned', 'scheduled', 'cancelled',
    'delivered', 'accepted', 'in_qa', 'refused', 'perm_refused')
    ) as orders JOIN

    (SELECT i.id, i.state, i.title
    FROM items as i JOIN projects as p on i.id = p.id
    JOIN localroles as l on p.id = l.item_id
    WHERE l.principal_id = '{principal_id}' AND
    p.order_type = '{type}') as projects
    on orders.project_id = projects.id

    ) as active_orders GROUP BY
    active_orders.title,
    active_orders.project_id
    ORDER BY active_orders.title
    '''

    def query_params(self, query: str) -> str:
        """Apply query parameters based on request.

        This is supposed to be specialized by resource classes.

        :query: string with a query to be parametrized
        :returns: string with a query after adding parameters
        """
        principal_id = self.request.user.id
        return query.format(principal_id=principal_id, type='leadorder')

    def transform(self, data: list) -> list:
        """Transform data items after query execution

        :data: list of records to be transformed
        :returns: list of records after transformation
        """
        for item in data:
            project_id = item.pop('project_id')
            item['absolute_url'] = f'/projects/{project_id}'
        return data
