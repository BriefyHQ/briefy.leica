"""Views to handle Scouting Dashboards."""
from briefy.leica.models import Pool
from briefy.leica.models.dashboard.scouting import DashboardScoutingCountry
from briefy.leica.models.dashboard.scouting import DashboardScoutingProject
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
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
class DashboardScoutingCountryService(RESTService):
    """Dashboard Scouting: Country Service."""

    model = DashboardScoutingCountry
    friendly_name = model.__name__
    default_order_by = 'country'

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
class DashboardScoutingProjectService(RESTService):
    """Dashboard Scouting: Project Service."""

    model = DashboardScoutingProject
    friendly_name = model.__name__
    default_order_by = 'title'

    _columns_map = (
        {
            'field': 'title', 'label': 'Project',
            'type': 'text', 'url': '', 'filter': ''
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
    friendly_name = model.__name__
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
