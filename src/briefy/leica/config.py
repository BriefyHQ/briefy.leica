"""Briefy Leica config."""
from briefy.common.config import _queue_suffix
from prettyconf import config

# NewRelic
NEW_RELIC_LICENSE_KEY = config('NEW_RELIC_LICENSE_KEY', default='')

# Queue
LEICA_QUEUE = config(
    'LEICA_QUEUE',
    default='leica-{env}'.format(env=_queue_suffix)
)

FILE_PICKER_API_KEY = config('FILE_PICKER_API_KEY', default='')

# Buckets
UPLOAD_BUCKET = config(
    'UPLOAD_BUCKET',
    default='upload-{env}-briefy'.format(env=_queue_suffix)
)

IMAGE_BUCKET = config(
    'IMAGE_BUCKET',
    default='images-{env}-briefy'.format(env=_queue_suffix)
)

DATABASE_URL = config('DATABASE_URL',)

# Agoda custom config
AGODA_DELIVERY_GDRIVE = config('AGODA_DELIVERY_GDRIVE', default='')
