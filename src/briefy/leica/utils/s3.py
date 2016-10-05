"""S3 helpers."""
from botocore.exceptions import ClientError
from briefy.leica.config import DEIS_APP
from briefy.leica.config import IMAGE_BUCKET
from briefy.leica.config import UPLOAD_BUCKET

import boto3
import logging

logger = logging.getLogger('briefy.leica')


def move_key_between_buckets(key: str, source: str, dest: str) -> bool:
    """Move a file (key) between two S3 buckets.

    :param key: Path to data to be moved.
    :param source: Source bucket.
    :param dest: Destination bucket.
    :return: Status of the move.
    """
    status = False
    s3 = boto3.resource('s3')
    source_path = '{source}/{key}'.format(source=source, key=key)
    try:
        s3.Object(dest, key).copy_from(CopySource=source_path)
    except ClientError as e:
        if 'NoSuchKey' in str(e):
            logger.exception('Source key not found: {key}'.format(key=key))
    else:
        try:
            s3.Object(source, key).delete()
        except ClientError as e:
            logger.exception('Not able to delete: {key} from {source}'.format(
                key=key,
                source=source
            ))
        else:
            status = True
    return status


def move_asset_source_file(key: str) -> bool:
    """Move an asset source file from the upload bucket to the destination bucket.

    :param key: Path to data to be moved.
    :return: Status of the move.
    """
    status = False
    source = UPLOAD_BUCKET
    dest = IMAGE_BUCKET
    if DEIS_APP:
        # We run only if inside a DEIS environment
        status = move_key_between_buckets(key, source, dest)
    return status
