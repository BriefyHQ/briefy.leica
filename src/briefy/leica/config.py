"""Briefy Leica config."""
from briefy.common.config import _queue_suffix
from prettyconf import casts
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
LEICA_QUEUE = config('LEICA_QUEUE', default='leica-{0}'.format(_queue_suffix))

IMAGE_BUCKET = config(
    'IMAGE_BUCKET',
    default='images-{env}-briefy'.format(env=_queue_suffix)
)

DATABASE_URL = config('DATABASE_URL',)

# Agoda custom config
AGODA_DELIVERY_GDRIVE = config('AGODA_DELIVERY_GDRIVE', default='')


# Intercom
INTERCOM_APP_ID = config('INTERCOM_APP_ID', default='c4iuqr75')
INTERCOM_HASH_KEY = config('INTERCOM_HASH_KEY', default='2p3C2UgAWLxlHiuCGKwhCTzrrPWdMAAqIwN7W0Cf')

# Check if running under DEIS
DEIS_APP = config('DEIS_APP', default='')

# API Configs
API_USERNAME = config('API_USERNAME', default='rudazz@gmail.com')
API_PASSWORD = config('API_PASSWORD', default='testtest')

API_BASE = config('API_BASE', default='https://api.stg.briefy.co')
ROLLEIFLEX_USERNAME = config('ROLLEIFLEX_USERNAME', default='app@briefy.co')
ROLLEIFLEX_BASE = config(
    'ROLLEIFLEX_BASE',
    default='http://briefy-rolleiflex.briefy-rolleiflex'
)
LOGIN_ENDPOINT = config('LOGIN_ENDPOINT', default=API_BASE + '/login/email')
ROSETTA_ENDPOINT = config('ROSETTA_ENDPOINT', default=API_BASE + '/internal/rosetta')

FILES_BASE = 'https://files.briefy.co' if _queue_suffix == 'live' else 'https://files.stg.briefy.co'

# job tasks: cron hour and minute setting
CRON_HOUR_JOB_TASKS = config('CRON_HOUR_JOB_TASKS', default='*')
CRON_MINUTE_JOB_TASKS = config('CRON_MINUTE_JOB_TASKS', default='*/1')

# number of days before scheduled date to schedule
SCHEDULE_DAYS_LIMIT = config('SCHEDULE_DAYS_LIMIT', default=1)

# Cache
ENABLE_CACHE = config('ENABLE_CACHE', casts.Boolean(), default=False)

# default 48 hs
LATE_SUBMISSION_SECONDS = config('LATE_SUBMISSION_SECONDS', default='172800')
# default 3 day
LATE_SUBMISSION_MAX_DAYS = config('LATE_SUBMISSION_MAX_DAYS', default='3')

# default 24 hs
BEFORE_SHOOTING_SECONDS = config('LATE_SUBMISSION_SECONDS', default='86400')

# notifications task config
ENABLE_LATE_SUBMISSION_NOTIFY = config(
    'ENABLE_LATE_SUBMISSION_NOTIFY', casts.Boolean(), default=False
)
ENABLE_BEFORE_SHOOTING_NOTIFY = config(
    'ENABLE_BEFORE_SHOOTING_NOTIFY', casts.Boolean(), default=False
)
