"""Syncronize Assets."""
from briefy.leica import logger
from briefy.leica.models import Assignment
from briefy.leica.models import Image

import csv
import os
import transaction


S3_SOURCE_PREFIX = 'source/files/'
SENTINEL_PROFESSIONAL_UUID = 'ca6083a9-bc94-4309-be3c-a80a0d1f2370'


def import_assets(session, asset_rows):
    """Import assets."""
    previous_assignment_id = None
    created = updated = count = 0
    failed = []

    for assignment_id, professional_id, s3_path, image_size, image_width, image_height \
            in asset_rows:
        if assignment_id != previous_assignment_id:
            job = Assignment.query().get(assignment_id)
            previous_assignment_id = assignment_id

        if not professional_id and job.professional_id:
            professional_id = job.professional_id
        else:
            professional_id = professional_id if professional_id else SENTINEL_PROFESSIONAL_UUID

        filename = s3_path.split('/')[-1]
        title = filename.strip('-_ ')
        if title.lower().startswith(job.order.customer_order_id.lower()):
            title = title[len(job.order.customer_order_id):].strip(" -+")
        title = title.replace("_", " ")
        # source_path = os.path.join(S3_SOURCE_PREFIX, s3_path.lstrip('/'))

        new_asset = False
        # asset = Asset.query().filter_by(source_path=source_path).first()

        possible_duplicate = [asset for asset in job.assets if asset.filename == filename]
        if len(possible_duplicate) >= 1:
            asset = possible_duplicate[0]
            updated += 1
            if len(possible_duplicate) > 1:
                logger.error('Job "{0}" has duplicate assets with the name "{1}"'.format(
                    assignment_id, filename))
                with open('duplicate_asset_filename.csv', 'at') as file_:
                    wr = csv.writer(file_)
                    wr.writerow((assignment_id, filename))
                del wr, file_
        else:
            created += 1
            new_asset = True
            asset = Image()

            # Main data updating:
            asset.update(dict(
                assignment_id=assignment_id,
                title=title,
                type='image',
                description="",
                content_type='image/jpeg',
                owner=str(professional_id),
                professional_id=professional_id,
                uploaded_by=professional_id,
                #  Image Mixin fields:
                source_path=os.path.join(S3_SOURCE_PREFIX, s3_path.lstrip('/')),
                filename=filename,
                size=image_size,
                width=image_width,
                height=image_height)
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

        savepoint = transaction.savepoint()
        try:
            if new_asset:
                session.add(asset)
            session.flush()
            print(".", end='', flush=True)
        except Exception as error:
            logger.error('Could not import asset "{}". Error {}'.format(
                s3_path, error))
            savepoint.rollback()
            failed.append(dict(assignment_id=job.id, asset_name=filename))
            continue

            count += 1
            if not count % 70:
                print()

    logger.info('{0} new assets imported into Leica'.format(created))
    logger.info('{0} new assets updated into Leica'.format(updated))
    return {'created': created, 'updated': updated, 'failed': failed}
