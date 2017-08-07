"""Views to handle Scouting Dashboards."""
from briefy.leica.models import Pool
from briefy.leica.models.dashboard.scouting import DashboardScoutingCountry
from briefy.leica.models.dashboard.scouting import DashboardScoutingProject
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources import SQLQueryService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


class DashboardScoutingCountryFactory(BaseFactory):
    """Dashboard Scouting Country context factory."""

    model = DashboardScoutingCountry

    __base_acl__ = [
        (Allow, 'g:briefy_scout', ['list', 'view']),
    ]


COLLECTION_PATH = '/dashboards/scouting/country'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardScoutingCountryFactory)
class DashboardScoutingCountryService(SQLQueryService):
    """Dashboard Scouting: Country Service."""

    _columns_map = (
        {
            'field': 'country', 'label': 'Country',
            'type': 'country', 'url': '', 'filter': ''
        },
        {
            'field': 'total', 'label': 'Total',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'unassigned', 'label': 'Manually Assign',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'pool', 'label': 'In Pool',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'assigned', 'label': 'Assigned',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'professionals', 'label': 'Photographers in Country',
            'type': 'integer', 'url': '', 'filter': ''
        },
    )

    _collection_query = """
    SELECT
    assignments_country.total,
    assignments_country.country,
    assignments_country.unassigned,
    assignments_country.pool,
    assignments_country.assigned,
    wk_locations.total_professionals as professionals

    FROM

    (SELECT

    count(assignments.id) as total,
    assignments.country,

    sum(
    CASE WHEN assignments.state = 'pending'
    THEN 1 ELSE 0
    END) as unassigned,

    sum(
    CASE WHEN
    assignments.state = 'published'
    AND assignments.pool_id IS NOT NULL
    THEN 1 ELSE 0
    END) as pool,

    sum(
    CASE WHEN
    assignments.state IN ('assigned', 'scheduled')
    THEN 1 ELSE 0
    END) as assigned

    FROM

    (SELECT DISTINCT
    i.id, i.state, a.pool_id, ol.country
    FROM items as i
    JOIN assignments as a on i.id = a.id
    JOIN orders as o on a.order_id = o.id
    JOIN orderlocations as ol on ol.order_id = o.id
    JOIN projects as p on o.project_id = p.id
    JOIN localroles as l on l.item_id = p.id
    WHERE
    i.state IN ('pending', 'published', 'assigned', 'scheduled')
    AND o.current_type = 'order'
    AND l.principal_id = '{principal_id}'
    AND l.role_name = 'internal_scout'
    ) as assignments

    GROUP BY assignments.country) as assignments_country JOIN

    (SELECT
    country,
    count(professional_id) as total_professionals
    FROM workinglocations
    GROUP BY country) as wk_locations
    on assignments_country.country = wk_locations.country

    ORDER BY assignments_country.country
    """

    def query_params(self, query: str) -> str:
        """Apply query parameters based on request.

        This is supposed to be specialized by resource classes.

        :query: string with a query to be parametrized
        :returns: string with a query after adding parameters
        """
        principal_id = self.request.user.id
        return query.format(principal_id=principal_id)


class DashboardScoutingProjectFactory(BaseFactory):
    """Dashboard Scouting Project context factory."""

    model = DashboardScoutingProject

    __base_acl__ = [
        (Allow, 'g:briefy_scout', ['list', 'view']),
    ]


COLLECTION_PATH = '/dashboards/scouting/project'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardScoutingProjectFactory)
class DashboardScoutingProjectService(SQLQueryService):
    """Dashboard Scouting: Project Service."""

    _columns_map = (
        {
            'field': 'absolute_url', 'label': 'url',
            'type': 'hidden', 'url': '', 'filter': ''
        },
        {
            'field': 'title', 'label': 'Project',
            'type': 'text', 'url': 'absolute_url', 'filter': ''
        },
        {
            'field': 'total', 'label': 'Total',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'unassigned', 'label': 'Manually Assign',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'pool', 'label': 'In Pool',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'assigned', 'label': 'Assigned',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'professionals', 'label': 'Active Photographers in Project',
            'type': 'integer', 'url': '', 'filter': ''
        },
    )

    _collection_query = """
    SELECT
    active_assignments.project_id,
    active_assignments.title,
    count(active_assignments.id) as total,

    sum(
    CASE WHEN active_assignments.state = 'pending'
    THEN 1 ELSE 0
    END) as unassigned,

    sum(
    CASE WHEN active_assignments.state = 'published'
    AND active_assignments.pool_id is not NULL
    THEN 1 ELSE 0
    END) as pool,

    sum(
    CASE WHEN
    active_assignments.state IN ('assigned', 'scheduled')
    THEN 1 ELSE 0
    END) as assigned,

    count(DISTINCT active_assignments.professional_id) as professionals

    FROM

    (SELECT DISTINCT
    projects.title,
    assignments.project_id,
    assignments.id,
    assignments.state,
    assignments.pool_id,
    assignments.professional_id

    FROM

    (SELECT i.id, i.state, a.pool_id, a.professional_id, o.project_id
    FROM items as i
    JOIN assignments as a on i.id = a.id
    JOIN orders as o on a.order_id = o.id
    JOIN localroles as l on l.item_id = a.id
    WHERE i.state IN ('pending', 'published', 'assigned', 'scheduled')
    AND o.current_type = 'order'
    ) as assignments JOIN

    (SELECT i.id, i.state, i.title
    FROM items as i JOIN projects as p on i.id = p.id
    JOIN localroles as l on p.id = l.item_id
    WHERE l.principal_id = '{principal_id}'
    AND l.role_name = 'internal_scout'
    ) as projects on assignments.project_id = projects.id

    ) as active_assignments

    GROUP BY active_assignments.title, active_assignments.project_id
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

    def transform(self, data: list) -> list:
        """Transform data items after query execution.

        :data: list of records to be transformed
        :returns: list of records after transformation
        """
        for item in data:
            project_id = item.pop('project_id')
            item['absolute_url'] = f'/projects/{project_id}'
        return data


class DashboardScoutingPoolFactory(BaseFactory):
    """Dashboard Scouting context factory."""

    model = Pool


COLLECTION_PATH = '/dashboards/scouting/pool'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardScoutingPoolFactory)
class DashboardScoutingPoolService(RESTService):
    """Dashboard Scouting: Pool Service."""

    model = Pool
    default_order_by = 'title'

    _columns_map = (
        {
            'field': 'title', 'label': 'Pool',
            'type': 'text', 'url': '', 'filter': ''
        },
        {
            'field': 'country', 'label': 'Country',
            'type': 'country', 'url': '', 'filter': ''
        },
        {
            'field': 'total_assignments', 'label': 'Total Assignments',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'live_assignments', 'label': 'Live Assignments',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'total_professionals', 'label': 'Number of Photographers',
            'type': 'integer', 'url': '', 'filter': ''
        },
    )
