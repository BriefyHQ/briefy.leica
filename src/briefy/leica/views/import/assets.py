"""Service to import batch add assets to briefy.leica."""
from briefy.ws import CORS_POLICY
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.authentication import Everyone
from pyramid.authorization import Allow
from briefy.leica import logger
from briefy.leica.models import Job
from briefy.leica.models import Asset

import json
import logging
import os
import transaction


S3_SOURCE_PREFIX = 'source/files/'
SENTINEL_PROFESSIONAL_UUID = 'ca6083a9-bc94-4309-be3c-a80a0d1f2370'


class ImportAssetsFactory(BaseFactory):
    """Internal context factory for import assets service."""

    @property
    def __base_acl__(self):
        """RosettaFactory custom acl.

        :return list of acl for the current logged user plus defaults.
        :rtype list
        """
        return [
            (Allow, Everyone, ['view', 'list', 'add']),
        ]


@resource(path='/internal/assets/import',
          cors_policy=CORS_POLICY,
          factory=ImportAssetsFactory)
class ImportAssetService:
    """Service to map knack profile ID to local user UUID."""

    def __init__(self, context, request):
        """Service initialize."""
        self.context = context
        self.request = request

    def post(self):
        """Return all profile IDs from knack mapped to respective user UUIDs."""
        success = False
        data = self.request.get('data')
        data = json.loads(data)
        if success:
            return {
                'status': 'success',
                'message': 'All assets upload success.',
                'data': data,
            }
        else:
            self.request.response.status_code = 400
            return {
                'status': 'error',
                'message': 'Failure to upload assets.'
            }

    def import_assets(self, asset_rows):
        """Import assets to database."""
        db = self.request.db
        previous_job_id = None
        created = updated = count = 0
        for job_id, s3_path in asset_rows:
            if job_id != previous_job_id:
                job = Job.query().get(job_id)
                previous_job_id = job_id

            if job.professional:
                professional_id = job.professional_id
            else:
                professional_id = SENTINEL_PROFESSIONAL_UUID

            title = s3_path.split('/')[-1]
            title = title.strip('-_ ')
            if title.lower().startswith(job.customer_job_id.lower()):
                title = title[len(job.customer_job_id):].strip(" -+")
            title = title.replace("_", " ")
            source_path = os.path.join(S3_SOURCE_PREFIX, s3_path.lstrip('/'))

            new_asset = False
            asset = Asset.query().filter_by(source_path=source_path).first()

            if not asset:
                created += 1
                new_asset = True
                asset = Asset()
            else:
                updated += 1
            asset.update(
                job_id=job_id,
                title=title,
                description="",
                # TODO: replace these with actual Photographer's names
                owner=str(professional_id),
                author_id=professional_id,
                uploaded_by=professional_id,
                #  Image Mixin fields:
                source_path=os.path.join(S3_SOURCE_PREFIX, s3_path.lstrip('/')),
                filename=s3_path.split('/')[-1]
            )
            asset.state = 'delivered'
            if asset.state_history and len(asset.state_history) == 1:
                # TODO: the information about photo uploading time can
                # be derived about JOB information on KnackHQ
                # (last_photographer_iteration, for example) -
                # as well as the correct transition date to delivered
                # these could be updated in a subsequent step.

                asset.state_history[0]['message'] = 'Imported in this state from Knack database'
                asset.state_history[0]['actor'] = ''
                asset.state_history[0]['to'] = asset.state

            with transaction.manager:
                try:
                    if new_asset:
                        db.add(asset)
                    db.flush()
                    print(".", end='', flush=True)
                except Exception as error:
                    logging.error('Could not import asset "{}". Error {}'.format(s3_path, error))
                    db.rollback()
                    continue
                count += 1
                if not count % 70:
                    print()
        logger.info('{} new assets imported into Leica'.format(created))
        logger.info('{} new assets updated into Leica'.format(updated))
