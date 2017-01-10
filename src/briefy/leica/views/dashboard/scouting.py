"""Views to handle Scouting Dashboards creation."""
from briefy.leica.models import Pool
from briefy.leica.models.dashboard.scouting import DashboardScoutingCountry
from briefy.leica.models.dashboard.scouting import DashboardScoutingProject
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from cornice.resource import view
from pyramid.security import Allow


COLLECTION_PATH = '/dashboards/scouting/country'
PATH = COLLECTION_PATH + '/{id}'


class DashboardScoutingFactory(BaseFactory):
    """DashboardScoutingCountry context factory."""

    model = DashboardScoutingCountry

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:briefy_scout', ['list']),
        ]
        return _acls


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardScoutingFactory)
class DashboardScoutingCountryService(RESTService):
    """Dashboard Scouting: Country Service."""

    model = DashboardScoutingCountry
    friendly_name = model.__name__
    default_order_by = 'country'

    column_map = (
        ('country', {'label': 'Country', 'type': 'country', 'url': '', 'filter': ''}),
        ('total', {'label': 'Total', 'type': 'integer', 'url': '', 'filter': ''}),
        ('unassigned', {'label': 'Unassigned Jobs', 'type': 'integer', 'url': '', 'filter': ''}),
        ('job_pool', {'label': 'In Job Pool', 'type': 'integer', 'url': '', 'filter': ''}),
        ('assigned', {'label': 'Assigned Jobs', 'type': 'integer', 'url': '', 'filter': ''}),
        ('professionals',
         {'label': 'Photographers in Country', 'type': 'integer', 'url': '', 'filter': ''}
         ),
    )

    @view(validators='_run_validators', permission='list')
    def collection_get(self):
        """Return a list of objects.

        :returns: Payload with total records and list of objects
        """
        headers = self.request.response.headers
        pagination = self.get_records()
        total = pagination['total']
        headers['Total-Records'] = '{total}'.format(total=total)
        # Force in here to use the listing serialization.
        pagination['data'] = [o.to_listing_dict() for o in pagination['data']]
        if self.column_map:
            pagination['columns'] = [{key: value} for key, value in self.column_map]
        return pagination


COLLECTION_PATH = '/dashboards/scouting/project'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardScoutingFactory)
class DashboardScoutingProjectService(RESTService):
    """Dashboard Scouting: Project Service."""

    model = DashboardScoutingProject
    friendly_name = model.__name__
    default_order_by = 'title'

    column_map = (
        ('project', {'label': 'Project', 'type': 'text', 'url': '', 'filter': ''}),
        ('total', {'label': 'Total', 'type': 'integer', 'url': '', 'filter': ''}),
        ('unassigned', {'label': 'Unassigned Jobs', 'type': 'integer', 'url': '', 'filter': ''}),
        ('job_pool', {'label': 'In Job Pool', 'type': 'integer', 'url': '', 'filter': ''}),
        ('assigned', {'label': 'Assigned Jobs', 'type': 'integer', 'url': '', 'filter': ''}),
        ('professionals',
         {'label': 'Active Photographers in Project', 'type': 'integer', 'url': '', 'filter': ''}
         ),
    )

    @view(validators='_run_validators', permission='list')
    def collection_get(self):
        """Return a list of objects.

        :returns: Payload with total records and list of objects
        """
        headers = self.request.response.headers
        pagination = self.get_records()
        total = pagination['total']
        headers['Total-Records'] = '{total}'.format(total=total)
        # Force in here to use the listing serialization.
        pagination['data'] = [o.to_listing_dict() for o in pagination['data']]
        if self.column_map:
            pagination['columns'] = [{key: value} for key, value in self.column_map]
        return pagination


COLLECTION_PATH = '/dashboards/scouting/pool'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardScoutingFactory)
class DashboardScoutingPoolService(RESTService):
    """Dashboard Scouting: Pool Service."""

    model = Pool
    friendly_name = model.__name__
    default_order_by = 'title'

    column_map = (
        ('pool', {'label': 'Pool', 'type': 'text', 'url': '', 'filter': ''}),
        ('country', {'label': 'Country', 'type': 'country', 'url': '', 'filter': ''}),
        ('total_assignments',
         {'label': 'Total Assignments', 'type': 'integer', 'url': '', 'filter': ''}
         ),
        ('live_assignments',
         {'label': 'Live Assignments', 'type': 'integer', 'url': '', 'filter': ''}
         ),
        ('total_professionals',
         {'label': 'Number of Photographers', 'type': 'integer', 'url': '', 'filter': ''}
         ),
    )

    @view(validators='_run_validators', permission='list')
    def collection_get(self):
        """Return a list of objects.

        :returns: Payload with total records and list of objects
        """
        headers = self.request.response.headers
        pagination = self.get_records()
        total = pagination['total']
        headers['Total-Records'] = '{total}'.format(total=total)
        # Force in here to use the listing serialization.
        pagination['data'] = [o.to_listing_dict() for o in pagination['data']]
        if self.column_map:
            pagination['columns'] = [{key: value} for key, value in self.column_map]
        return pagination
