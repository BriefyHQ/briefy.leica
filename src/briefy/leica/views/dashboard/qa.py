"""Views to handle QA Dashboards."""
from briefy.leica.models.dashboard.qa import DashboardQaProject
from briefy.leica.models.dashboard.qa import DashboardQaType
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
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
class DashboardQaTypeService(RESTService):
    """Dashboard Qa: Type Service."""

    model = DashboardQaType
    friendly_name = model.__name__
    default_order_by = 'total'

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
class DashboardQaProjectService(RESTService):
    """Dashboard Qa: Project Service."""

    model = DashboardQaProject
    friendly_name = model.__name__
    default_order_by = 'title'

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
