"""Service to import batch add assets to briefy.leica."""
from briefy.leica import logger
from briefy.leica.tools.asset_import import import_assets
from briefy.ws import CORS_POLICY
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from cornice.resource import view
from pyramid.authentication import Everyone
from pyramid.authorization import Allow


class AssetImportFactory(BaseFactory):
    """Internal context factory for import assets service."""

    @property
    def __base_acl__(self):
        """AssetImportFactory custom acl.

        :return list of acl for the current logged user plus defaults.
        :rtype list
        """
        return [
            (Allow, Everyone, ['view', 'list', 'add']),
        ]


@resource(path='/assets/import',
          cors_policy=CORS_POLICY,
          factory=AssetImportFactory)
class AssetImportService:
    """Service to import assets from knack to briefy.leica."""

    def __init__(self, context, request):
        """Service initialize."""
        self.context = context
        self.request = request

    @view(permission='add')
    def post(self):
        """Add all assets from the data list received as a json map."""
        data = self.request.json.get('data')
        success = False
        result = {}

        if data:
            asset_rows = []
            for item in data:
                asset_rows.append(
                    (item['job_id'], item['s3_path'], item['image_size'],
                     item['image_width'], item['image_height'])
                )
            session = self.request.db
            try:
                result = import_assets(session, asset_rows)
            except Exception as exc:
                success = False
                logger.info('Exception: {exc}'.format(exc=exc))
            else:
                success = True

        if success:
            return {
                'status': 'success',
                'message': 'All assets uploaded success.',
                'data': result,
            }
        else:
            self.request.response.status_code = 400
            return {
                'status': 'error',
                'message': 'Failure to upload assets.'
            }
