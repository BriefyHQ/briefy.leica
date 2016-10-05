"""Test imaging utilities."""
from briefy.leica.utils import s3
from moto import mock_s3

import boto3


@mock_s3
def test_move_key_between_buckets():
    """Test move_key_between_buckets."""
    func = s3.move_key_between_buckets
    data = b'Hello world!!'
    key = 'foo/bar/hello.txt'

    # Setup
    client = boto3.resource('s3')

    client.create_bucket(Bucket='source')
    source = client.Bucket('source')

    client.create_bucket(Bucket='dest')
    dest = client.Bucket('dest')

    client.Object('source', key).put(Body=data)

    assert len([o for o in source.objects.all()]) == 1
    assert len([o for o in dest.objects.all()]) == 0

    status = func(key, 'source', 'dest')

    assert status is True
    assert len([o for o in source.objects.all()]) == 0
    assert len([o for o in dest.objects.all()]) == 1


@mock_s3
def test_move_key_between_buckets_key_not_found():
    """Test move_key_between_buckets with a wrong key."""
    func = s3.move_key_between_buckets
    key = 'foo/bar/hello.txt'

    # Setup
    client = boto3.resource('s3')

    client.create_bucket(Bucket='source')
    client.create_bucket(Bucket='dest')

    status = func(key, 'source', 'dest')

    assert status is False


@mock_s3
def test_move_asset_source_file():
    """Test move_asset_source_file."""
    from briefy.leica.config import IMAGE_BUCKET
    from briefy.leica.config import UPLOAD_BUCKET

    func = s3.move_asset_source_file
    data = b'Hello world!!'
    key = 'foo/bar/hello.txt'

    # Setup
    client = boto3.resource('s3')

    client.create_bucket(Bucket=UPLOAD_BUCKET)
    source = client.Bucket(UPLOAD_BUCKET)

    client.create_bucket(Bucket=IMAGE_BUCKET)
    dest = client.Bucket(IMAGE_BUCKET)

    client.Object(UPLOAD_BUCKET, key).put(Body=data)

    assert len([o for o in source.objects.all()]) == 1
    assert len([o for o in dest.objects.all()]) == 0

    status = func(key)

    assert status is True
    assert len([o for o in source.objects.all()]) == 0
    assert len([o for o in dest.objects.all()]) == 1