"""Service to import batch add assets to briefy.leica."""
from briefy.leica import logger
from briefy.leica.sync.customer import CustomerSync
from briefy.leica.sync.job import JobSync
from briefy.leica.sync.project import ProjectSync
from briefy.ws import CORS_POLICY
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from cornice.resource import view
from pyramid.authentication import Everyone
from pyramid.authorization import Allow


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
        session = self.request.db
        msg = '{model} - created: {created} | updated: {updated}'

        customers_created, customers_updated = CustomerSync(session)()
        logger.info(msg.format(
            model='Customers',
            created=len(customers_created),
            updated=len(customers_updated)
        ))

        projects_created, projects_updated = ProjectSync(session)()
        logger.info(msg.format(
            model='Projects',
            created=len(projects_created),
            updated=len(projects_updated)
        ))

        jobs_created, jobs_updated = JobSync(session)()
        logger.info(msg.format(
            model='Jobs',
            created=len(jobs_created),
            updated=len(jobs_updated)
        ))

        result = dict(
            jobs={'created': len(jobs_created), 'updated': len(jobs_updated)},
            customers={'created': len(customers_created), 'updated': len(customers_updated)},
            projects={'created': len(projects_created), 'updated': len(projects_updated)},
        )

        return {
            'status': 'success',
            'result': result
        }
