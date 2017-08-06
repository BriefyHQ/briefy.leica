"""Views to handle Customer Dashboards."""
from briefy.leica.models.dashboard.customer import DashboardCustomerAllLeads
from briefy.leica.models.dashboard.customer import DashboardCustomerAllOrders
from briefy.leica.models.dashboard.customer import DashboardCustomerDeliveredOrders
from briefy.leica.views.dashboard import DASHBOARD_ALL_ORDERS_CUSTOMER_QUERY
from briefy.leica.views.dashboard import DELIVERED_ORDERS_COLS
from briefy.leica.views.dashboard import LEAD_PROJECT_COLS
from briefy.leica.views.dashboard import ORDER_PROJECT_COLS
from briefy.ws import CORS_POLICY
from briefy.ws.resources import SQLQueryService
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
class DashboardCustomerAllOrdersService(SQLQueryService):
    """Dashboard Customer: All Orders Service."""

    model = DashboardCustomerAllOrders
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
class DashboardCustomerDeliveredOrderService(SQLQueryService):
    """Dashboard Customer: Delivered Orders Service."""

    model = DashboardCustomerDeliveredOrders
    default_order_by = 'title'

    _columns_map = DELIVERED_ORDERS_COLS

    _collection_query = """
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

    (SELECT i.id, i.state, i.title, p.customer_id
    FROM items as i JOIN projects as p on i.id = p.id) as projects
    on orders.project_id = projects.id JOIN
    
    (SELECT i.id, i.state, i.title
    FROM items as i JOIN customers as c on i.id = c.id
    JOIN localroles as l on c.id = l.item_id
    WHERE l.principal_id = '{principal_id}') as customers
    on projects.customer_id = customers.id

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
class DashboardCustomerAllLeadsService(SQLQueryService):
    """Dashboard Customer: All Leads Service."""

    model = DashboardCustomerAllLeads
    default_order_by = 'title'

    _columns_map = LEAD_PROJECT_COLS

    _collection_query = """
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
    JOIN leadorders as l on l.id = o.id
    WHERE i.type = '{type}' AND
    i.state IN ('new', 'received', 'assigned', 'scheduled', 'cancelled',
    'delivered', 'accepted', 'in_qa', 'refused', 'perm_refused')
    ) as orders JOIN

    (SELECT i.id, i.state, i.title, p.customer_id
    FROM items as i JOIN projects as p on i.id = p.id
    WHERE p.order_type = '{type}') as projects
    on orders.project_id = projects.id JOIN
    
    (SELECT i.id, i.state, i.title
    FROM items as i JOIN customers as c on i.id = c.id
    JOIN localroles as l on c.id = l.item_id
    WHERE l.principal_id = '{principal_id}') as customers
    on projects.customer_id = customers.id

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
        return query.format(principal_id=principal_id, type='leadorder')

    def transform(self, data: list) -> list:
        """Transform data items after query execution.

        :data: list of records to be transformed
        :returns: list of records after transformation
        """
        for item in data:
            project_id = item.pop('project_id')
            item['absolute_url'] = f'/projects/{project_id}'
        return data
