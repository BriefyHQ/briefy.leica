"""Views to handle QA Dashboards."""
from briefy.leica.models.dashboard.qa import DashboardQaType
from briefy.leica.models.dashboard.qa import DashboardQaProject
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


class DashboardQaFactory(BaseFactory):
    """Dashboard QA context factory."""

    model = DashboardQaType

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:briefy_qa', ['list']),
        ]
        return _acls


COLLECTION_PATH = '/dashboards/qa/type'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardQaFactory)
class DashboardQaTypeService(RESTService):
    """Dashboard Qa: Type Service."""

    model = DashboardQaType
    friendly_name = model.__name__
    default_order_by = 'total'

    _columns_map = (
        ('total',
         {'label': 'Sets awaiting approval in Total', 'type': 'integer', 'url': '', 'filter': ''}
         ),
        ('refused_customer',
         {'label': 'Sets Refused By Client', 'type': 'integer', 'url': '', 'filter': ''}
         ),
        ('returned_photographer',
         {'label': 'Sets Returned from Photographer', 'type': 'integer', 'url': '', 'filter': ''}
         ),
        ('new',
         {'label': 'New Sets', 'type': 'integer', 'url': '', 'filter': ''}
         ),
    )


COLLECTION_PATH = '/dashboards/qa/project'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardQaFactory)
class DashboardQaProjectService(RESTService):
    """Dashboard Qa: Project Service."""

    model = DashboardQaProject
    friendly_name = model.__name__
    default_order_by = 'title'

    _columns_map = (
        ('title',
         {'label': 'Project Name', 'type': 'text', 'url': '', 'filter': ''}
         ),
        ('refused_customer',
         {'label': 'Sets Refused', 'type': 'integer', 'url': '', 'filter': ''}
         ),
        ('returned_photographer',
         {'label': 'Sets Returned', 'type': 'integer', 'url': '', 'filter': ''}
         ),
        ('job_pool',
         {'new': 'New Sets', 'type': 'integer', 'url': '', 'filter': ''}
         ),
        ('total',
         {'label': 'In Total', 'type': 'integer', 'url': '', 'filter': ''}
         ),
    )
