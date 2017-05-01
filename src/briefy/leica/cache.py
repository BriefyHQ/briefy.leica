"""Initial briefy.leica cache configuration."""
from briefy.common.cache import ICacheManager
from zope.component import getUtility


cache_manager = getUtility(ICacheManager)
region = cache_manager.region()
