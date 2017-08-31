"""Views to handle Professional Dashboards."""
from briefy.leica.models.dashboard.professional import DashboardProfessionalAssignment
from briefy.ws import CORS_POLICY
from briefy.ws.resources import SQLQueryService
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
class DashboardProfessionalAssignmentService(SQLQueryService):
    """Dashboard Professional: Assignment Service."""

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
            'field': 'awaiting_submission_resubmission',
            'label': 'Waiting Submission / Resubmission',
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

    _collection_query = """
    SELECT
    count(active_assignments.id) as total,

    sum(
    CASE WHEN
    active_assignments.state = 'assigned'
    THEN 1 ELSE 0
    END) as assigned,

    sum(
    CASE WHEN active_assignments.state = 'scheduled'
    THEN 1 ELSE 0
    END) as scheduled,

    sum(
    CASE WHEN active_assignments.state = 'awaiting_assets'
    THEN 1 ELSE 0
    END) as awaiting_submission_resubmission,

    sum(
    CASE WHEN active_assignments.state IN ('in_qa', 'asset_validation')
    THEN 1 ELSE 0
    END) as in_qa,

    sum(
    CASE WHEN
    active_assignments.state IN ('approved', 'completed', 'perm_rejected', 'cancelled', 'refused')
    THEN 1 ELSE 0
    END) as completed_inactive

    FROM

    (SELECT DISTINCT assignments.id, assignments.state FROM

    (SELECT i.id, i.state, i.title
    FROM items as i
    JOIN assignments as a on i.id = a.id
    JOIN localroles as l on l.item_id = a.id
    WHERE i.state IN ('assigned', 'scheduled', 'in_qa', 'approved', 'completed',
    'perm_rejected', 'refused', 'cancelled', 'awaiting_assets', 'asset_validation')
    AND l.principal_id = '{principal_id}'
    AND l.role_name = 'professional_user'
    ) as assignments

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
