"""Initial briefy.leica cache configuration."""
from briefy.common.cache import ICacheManager
from briefy.leica.config import ENABLE_CACHE
from zope.component import getUtility


def enable_cache(*args, **kwargs) -> bool:
    """Return True if cache enable, else False."""
    return ENABLE_CACHE


cache_manager = getUtility(ICacheManager)
cache_region = cache_manager.region()
