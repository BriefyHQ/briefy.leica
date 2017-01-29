"""Views to handle BizDev Dashboards."""
from briefy.leica.models.dashboard.bizdev import DashboardBizDevOrder
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
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
class DashboardBizDevOrderService(RESTService):
    """Dashboard BizDev: Order Service."""

    model = DashboardBizDevOrder
    friendly_name = model.__name__
    default_order_by = 'title'

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
            'field': 'total', 'label': 'All Orders',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'received', 'label': 'New Orders',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'assigned', 'label': 'Assigned Orders',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'scheduled', 'label': 'Scheduled Orders',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'in_qa', 'label': 'Orders in QA process',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'cancelled', 'label': 'Cancelled Orders',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'completed', 'label': 'Completed Orders',
            'type': 'integer', 'url': '', 'filter': ''
        }
    )
