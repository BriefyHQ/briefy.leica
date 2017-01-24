"""Briefy Leica config."""
from briefy.common.config import _queue_suffix
from prettyconf import config

# NewRelic
NEW_RELIC_LICENSE_KEY = config('NEW_RELIC_LICENSE_KEY', default='')

# FilePick
FILE_PICKER_API_KEY = config('FILE_PICKER_API_KEY', default='')

# Buckets
UPLOAD_BUCKET = config(
    'UPLOAD_BUCKET',
    default='upload-{env}-briefy'.format(env=_queue_suffix)
)

# Queue
LEICA_QUEUE = config('LEICA_QUEUE', default='leica-{}'.format(_queue_suffix))

IMAGE_BUCKET = config(
    'IMAGE_BUCKET',
    default='images-{env}-briefy'.format(env=_queue_suffix)
)

DATABASE_URL = config('DATABASE_URL',)

# Agoda custom config
AGODA_DELIVERY_GDRIVE = config('AGODA_DELIVERY_GDRIVE', default='')

# Check if running under DEIS
DEIS_APP = config('DEIS_APP', default='')

# API Configs
API_USERNAME = config('API_USERNAME', default='rudazz@gmail.com')
API_PASSWORD = config('API_PASSWORD', default='testtest')

API_BASE = config('API_BASE', default='https://api.stg.briefy.co')
LOGIN_ENDPOINT = config('LOGIN_ENDPOINT', default=API_BASE + '/login/email')
ROSETTA_ENDPOINT = config('ROSETTA_ENDPOINT', default=API_BASE + '/internal/rosetta')

FILES_BASE = 'https://files.briefy.co' if _queue_suffix == 'live' else 'https://files.stg.briefy.co'
