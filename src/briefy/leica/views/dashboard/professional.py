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

    __base_acl__ = [
        (Allow, 'g:professionals', ['list', 'view']),
    ]


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
        {
            'field': 'total', 'label': 'All your Assignments',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'assigned', 'label': 'To be Scheduled',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'scheduled', 'label': 'Scheduled',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'awaiting_submission_resubmission', 'label': 'Waiting Submission / Resubmission',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'in_qa', 'label': 'In QA Review',
            'type': 'integer', 'url': '', 'filter': ''
        },
        {
            'field': 'completed_inactive', 'label': 'Completed / Inactive',
            'type': 'integer', 'url': '', 'filter': ''
        }
    )

    def default_filters(self, query) -> object:
        """Default filters to be applied to every query.

        This is supposed to be specialized by resource classes.
        :returns: A tuple of default filters to be applied to queries.
        """
        user = self.request.user
        query = query.params(professional_id_1=user.id)
        return query
