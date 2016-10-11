"""Service to import/sync customers and dependencies from knack to briefy.leica."""
from briefy.leica import logger
from briefy.leica.sync.customer import CustomerSync
from briefy.ws import CORS_POLICY
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from cornice.resource import view
from pyramid.authentication import Everyone
from pyramid.authorization import Allow


class CustomerImportFactory(BaseFactory):
    """Internal context factory for import customers service."""

    @property
    def __base_acl__(self):
        """CustomerImportFactory custom acl.

        :return list of acl for the current logged user plus defaults.
        :rtype list
        """
        return [
            (Allow, Everyone, ['view', 'list', 'add']),
        ]


@resource(collection_path='/customers/import',
          path='/customers/import/{knack_id}',
          cors_policy=CORS_POLICY,
          factory=CustomerImportFactory)
class CustomerImportService:
    """Service to import/sync customers from knack to briefy.leica."""

    def __init__(self, context, request):
        """Service initialize."""
        self.context = context
        self.request = request
        session = self.request.db
        self.customer_sync = CustomerSync(session)

    @view(permission='add')
    def collection_post(self):
        """Import/sync all existing Customers from knack to leica."""
        msg = '{model} - created: {created} | updated: {updated}'

        customers_created, customers_updated = self.customer_sync()
        logger.info(msg.format(
            model='Customers',
            created=len(customers_created),
            updated=len(customers_updated)
        ))

        result = dict(
            customers={'created': len(customers_created), 'updated': len(customers_updated)},
        )

        return {
            'status': 'success',
            'result': result
        }

    @view(permission='add')
    def post(self):
        """Add or update one Customer model from knack Company item."""
        knack_id = self.request.matchdict.get('knack_id')
        try:
            self.customer_sync(knack_id)
        except Exception as exc:
            msg = 'Failure updating knack Project: {knack_id}. Error: {exc}'.format(
                knack_id=knack_id,
                exc=exc
            )
            logger.error(msg)
            self.request.response.status_code = 400
            return dict(status='error', message=msg)
        else:
            msg = 'Success updating knack Project: {knack_id}'.format(knack_id=knack_id)
            return dict(status='success', mesage=msg)
