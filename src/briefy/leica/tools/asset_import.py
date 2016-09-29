from briefy.leica import logger
from briefy.leica.config import DATABASE_URL
from briefy.leica.db import Session  # noQA
from briefy.leica.db import create_engine
from briefy.leica.models import Job
from briefy.leica.models import Asset


# import briefy.leica as K
import csv
import logging
import os
import transaction
import uuid  # noQA


CSV_NAME = 's3_paths.csv'

S3_SOURCE_PREFIX = 'source/files/'

SENTINEL_PROFESSIONAL_UUID = 'ca6083a9-bc94-4309-be3c-a80a0d1f2370'

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
                    Session.add(asset)
                Session.flush()
                print(".", end='', flush=True)
            except Exception as error:
                logging.error('Could not import asset "{}". Error {}'.format(
                    s3_path, error))
                Session.rollback()
                continue

            count += 1
            if not count % 70:
                print()
    logging.info('{} new assets imported into Leica'.format(created))
    logging.info('{} new assets updated into Leica'.format(updated))

"""
def grab_data()
    global KJob, KPhotographer, all_jobs, all_photographers, kphoto_id, kjob_id
    KJob = K.get_model("Job")
    KPhotographer = K.get_model("Photographer")
    print('Downloading all Job and Professional information from KnackHQ')
    all_jobs = KJob.query.all()
    all_photographers = KPhotographer.query.all()

    kphoto_id = {p.id:p for p in all_photographers}
    kjob_id = {j.id:j for j in all_jobs}
"""


def main():
    """Handles all the stuff"""
    asset_reader = csv.reader(open(CSV_NAME))

    # Throw away headers:
    next(asset_reader)

    import_assets(asset_reader)

if __name__ == '__main__':
    main()
