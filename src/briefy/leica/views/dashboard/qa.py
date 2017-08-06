"""Views to handle QA Dashboards."""
from briefy.leica.models.dashboard.qa import DashboardQaProject
from briefy.leica.models.dashboard.qa import DashboardQaType
from briefy.ws import CORS_POLICY
from briefy.ws.resources import SQLQueryService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


class DashboardQaTypeFactory(BaseFactory):
    """Dashboard QA Type context factory."""

    model = DashboardQaType

    __base_acl__ = [
        (Allow, 'g:briefy_qa', ['list', 'view']),
    ]


COLLECTION_PATH = '/dashboards/qa/type'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardQaTypeFactory)
class DashboardQaTypeService(SQLQueryService):
    """Dashboard Qa: Type Service."""

    _columns_map = (
        {
            'field': 'total', 'label': 'Sets awaiting approval',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'new', 'label': 'New Sets',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'refused_customer', 'label': 'Sets Refused By Client',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'returned_photographer', 'label': 'Sets Returned from Photographer',
            'type': 'integer', 'url': '', 'filter': ''
        },
    )

    _collection_query = """
    SELECT
    count(active_assignments.id) as total,

    sum(
    CASE WHEN active_assignments.set_type = 'refused_customer'
    THEN 1 ELSE 0
    END) as refused_customer,

    sum(
    CASE WHEN active_assignments.set_type = 'returned_photographer'
    THEN 1 ELSE 0
    END) as returned_photographer,

    sum(
    CASE WHEN active_assignments.set_type = 'new'
    THEN 1 ELSE 0
    END) as new

    FROM

    (SELECT DISTINCT assignments.id, assignments.set_type FROM

    (SELECT i.id, a.set_type, o.project_id
    FROM items as i
    JOIN assignments as a on i.id = a.id
    JOIN orders as o on a.order_id = o.id
    JOIN localroles as l on l.item_id = a.id
    WHERE i.state = 'in_qa'
    ) as assignments JOIN

    (SELECT i.id, i.state, i.title
    FROM items as i JOIN projects as p on i.id = p.id
    JOIN localroles as l on p.id = l.item_id
    WHERE l.principal_id = '{principal_id}'
    AND l.role_name = 'internal_qa'
    ) as projects on assignments.project_id = projects.id

    ) as active_assignments ORDER BY total
    """

    def query_params(self, query: str) -> str:
        """Apply query parameters based on request.

        This is supposed to be specialized by resource classes.

        :query: string with a query to be parametrized
        :returns: string with a query after adding parameters
        """
        principal_id = self.request.user.id
        return query.format(principal_id=principal_id)


class DashboardQaProjectFactory(BaseFactory):
    """Dashboard QA Project context factory."""

    model = DashboardQaProject

    __base_acl__ = [
        (Allow, 'g:briefy_qa', ['list', 'view']),
    ]


COLLECTION_PATH = '/dashboards/qa/project'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardQaProjectFactory)
class DashboardQaProjectService(SQLQueryService):
    """Dashboard Qa: Project Service."""

    _columns_map = (
        {
            'field': 'title', 'label': 'Project Name',
            'type': 'text', 'url': '', 'filter': ''
        },
        {
            'field': 'refused_customer', 'label': 'Sets Refused',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'returned_photographer', 'label': 'Sets Returned',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'new', 'label': 'New Sets',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'total', 'label': 'In Total',
            'type': 'integer', 'url': '', 'filter': ''
        },
    )

    _collection_query = """
    SELECT
    active_assignments.title,
    count(active_assignments.id) as total,

    sum(
    CASE WHEN active_assignments.set_type = 'refused_customer'
    THEN 1 ELSE 0
    END) as refused_customer,

    sum(
    CASE WHEN active_assignments.set_type = 'returned_photographer'
    THEN 1 ELSE 0
    END) as returned_photographer,

    sum(
    CASE WHEN active_assignments.set_type = 'new'
    THEN 1 ELSE 0
    END) as new

    FROM

    (SELECT DISTINCT assignments.id, assignments.set_type, projects.title FROM

    (SELECT i.id, a.set_type, o.project_id
    FROM items as i
    JOIN assignments as a on i.id = a.id
    JOIN orders as o on a.order_id = o.id
    JOIN localroles as l on l.item_id = a.id
    WHERE i.state = 'in_qa'
    ) as assignments JOIN

    (SELECT i.id, i.state, i.title
    FROM items as i JOIN projects as p on i.id = p.id
    JOIN localroles as l on p.id = l.item_id
    WHERE l.principal_id = '{principal_id}'
    AND l.role_name = 'internal_qa'
    ) as projects on assignments.project_id = projects.id

    ) as active_assignments
    GROUP BY title
    ORDER BY title
    """

    def query_params(self, query: str) -> str:
        """Apply query parameters based on request.

        This is supposed to be specialized by resource classes.

        :query: string with a query to be parametrized
        :returns: string with a query after adding parameters
        """
        principal_id = self.request.user.id
        return query.format(principal_id=principal_id)
