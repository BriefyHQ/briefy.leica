"""Datetime utilities."""
from datetime import datetime
import pytz


def utc_now() -> datetime:
    """Return the current timezone-aware datetime."""
    now = datetime.utcnow()
    return now.replace(tzinfo=pytz.utc)
