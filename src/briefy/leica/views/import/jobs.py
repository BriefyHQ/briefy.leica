"""Service to import batch add assets to briefy.leica."""
from briefy.leica import logger
from briefy.leica.models import Customer
from briefy.leica.models import Project
from briefy.leica.models import Job
from briefy.leica.tools.knack_import import get_rosetta
from briefy.leica.tools.knack_import import import_projects
from briefy.leica.tools.knack_import import import_jobs
from briefy.ws import CORS_POLICY
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from cornice.resource import view
from pyramid.authentication import Everyone
from pyramid.authorization import Allow

import pycountry


class JobImportFactory(BaseFactory):
    """Internal context factory for import jobs service."""

    @property
    def __base_acl__(self):
        """JobImportFactory custom acl.

        :return list of acl for the current logged user plus defaults.
        :rtype list
        """
        return [
            (Allow, Everyone, ['view', 'list', 'add']),
        ]


@resource(path='/jobs/import',
          cors_policy=CORS_POLICY,
          factory=JobImportFactory)
class JobImportService:
    """Service to import jobs from knack to briefy.leica."""

    def __init__(self, context, request):
        """Service initialize."""
        self.context = context
        self.request = request

    @view(permission='add')
    def post(self):
        """Return all profile IDs from knack mapped to respective user UUIDs."""
        len(pycountry.countries)
        rosetta = get_rosetta()

        session = self.request.db
        project_dict = import_projects(session, rosetta)
        import_jobs(project_dict, session, rosetta)

        customers = Customer.query().count()
        projects = Project.query().count()
        jobs = Job.query().count()

        msg = 'Total of items: Customers: {customers}, ' \
              'Projects: {projects} and Jobs: {jobs} imported.'.format(customers=customers,
                                                                       projects=projects,
                                                                       jobs=jobs)
        logger.info(msg)

        return {
            'status': 'success',
            'message': msg
        }
