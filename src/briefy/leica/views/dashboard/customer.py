"""Views to handle Customer Dashboards."""
from briefy.leica.models.dashboard.customer import DashboardCustomerOrder
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


class DashboardCustomerFactory(BaseFactory):
    """Dashboard Customer context factory."""

    model = DashboardCustomerOrder

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:customers', ['list', 'view']),
        ]
        return _acls


COLLECTION_PATH = '/dashboards/customer/order'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardCustomerFactory)
class DashboardCustomerOrderService(RESTService):
    """Dashboard Customer: Order Service."""

    model = DashboardCustomerOrder
    friendly_name = model.__name__
    default_order_by = 'total'

    _columns_map = (
        {
            'field': 'title', 'label': 'Project',
            'type': 'text', 'url': '', 'filter': ''
        },
        {
            'field': 'total', 'label': 'Total Jobs',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'received', 'label': 'New Jobs',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'assigned', 'label': 'Jobs Assigned',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'scheduled', 'label': 'Jobs Scheduled',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'in_qa', 'label': 'Jobs in QA process',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'cancelled', 'label': 'Jobs Cancelled',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'completed', 'label': 'Jobs Completed',
            'type': 'integer', 'url': '', 'filter': ''
        }
    )

    @property
    def default_filters(self) -> tuple:
        """Default filters to be applied to every query.

        This is supposed to be specialized by resource classes.
        :returns: A tuple of default filters to be applied to queries.
        """
        # user = self.request.user
        filters = tuple()
        return filters
