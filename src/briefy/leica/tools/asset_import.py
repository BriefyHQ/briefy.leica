from briefy.leica import logger
from briefy.leica.config import DATABASE_URL
from briefy.leica.db import Session  # noQA
from briefy.leica.db import create_engine
from briefy.leica.models import Job
from briefy.leica.models import Asset

import csv
import logging
import os
import transaction


CSV_NAME = 's3_paths.csv'

S3_SOURCE_PREFIX = 'source/files/'

logger.setLevel(logging.DEBUG)
logger.handlers[0].setLevel(logging.DEBUG)


def configure():
    """Bind session for 'stand alone' DB usage"""
    global Session
    engine = create_engine(DATABASE_URL, pool_recycle=3600)
    Session.configure(bind=engine)
    return Session

Session = configure()  # noQA


class Auto:
    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)

    def __getattr__(self, attr):
        return ''


def import_assets(asset_rows):

    previous_job_id = None
    count = 0
    for job_id, s3_path in asset_rows:
        if job_id != previous_job_id:
            job = Job.query().get(job_id)
            previous_job_id = job_id

        title = s3_path.split('/')[-1]
        title = title.strip('-_ ')
        if title.lower().startswith(job.customer_job_id.lower()):
            title = title[len(job.customer_job_id):].strip(" -+")
        title = title.replace("_", " ")
        asset = Asset(
            job_id=job_id,
            title=title,
            description="",
            # TODO: replace these with actual Photographer's names
            owner=str(job.professional_id),
            author_id=job.professional_id,
            uploaded_by=job
            .professional_id,
            #  Image Mixin fields:
            source_path=os.path.join(S3_SOURCE_PREFIX, s3_path)
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
                Session.add(asset)
                Session.flush()
            except Exception as error:
                logging.error('Could not import asset "{}". Error {}'.format(
                    s3_path, error))
                Session.rollback()
                continue

            count += 1
    logging.info('{} new projects imported into Leica'.format(count))


def main():
    """Handles all the stuff"""

    asset_reader = csv.reader(open(CSV_NAME))

    # Throw away headers:
    next(asset_reader)

    import_assets(asset_reader)

if __name__ == '__main__':
    main()
