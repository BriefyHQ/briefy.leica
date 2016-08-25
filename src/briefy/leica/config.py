"""Briefy Leica config."""
from briefy.common.config import _queue_suffix
from prettyconf import config

# NewRelic
NEW_RELIC_LICENSE_KEY = config('NEW_RELIC_LICENSE_KEY', default='')

# Queue
LEICA_QUEUE = config('LEICA_QUEUE', default='leica-{}'.format(_queue_suffix))
