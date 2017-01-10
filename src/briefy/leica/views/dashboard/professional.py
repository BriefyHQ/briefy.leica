"""Views to handle Professional Dashboards."""
from briefy.leica.models.dashboard.professional import DashboardProfessionalAssignment
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


class DashboardProfessionalFactory(BaseFactory):
    """Dashboard Professional context factory."""

    model = DashboardProfessionalAssignment

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.

        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, 'g:professionals', ['list']),
        ]
        return _acls


COLLECTION_PATH = '/dashboards/professional/assignment'
PATH = COLLECTION_PATH + '/{id}'


@resource(collection_path=COLLECTION_PATH,
          path=PATH,
          cors_policy=CORS_POLICY,
          factory=DashboardProfessionalFactory)
class DashboardProfessionalAssignmentService(RESTService):
    """Dashboard Professional: Assignment Service."""

    model = DashboardProfessionalAssignment
    friendly_name = model.__name__
    default_order_by = 'total'

    _columns_map = (
        ('total',
         {'label': 'Total number of Jobs', 'type': 'integer', 'url': '', 'filter': ''}
         ),
        ('assigned',
         {'label': 'Jobs to be scheduled', 'type': 'integer', 'url': '', 'filter': ''}
         ),
        ('scheduled',
         {'label': 'Jobs scheduled', 'type': 'integer', 'url': '', 'filter': ''}
         ),
        ('in_qa',
         {'label': 'Jobs in QA process', 'type': 'integer', 'url': '', 'filter': ''}
         ),
        ('rejected',
         {'label': 'Jobs rejected by QA', 'type': 'integer', 'url': '', 'filter': ''}
         ),
        ('completed',
         {'label': 'Jobs completed', 'type': 'integer', 'url': '', 'filter': ''}
         ),
    )
