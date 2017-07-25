"""Datetime utilities."""
from datetime import datetime

import pytz


def utc_now() -> datetime:
    """Return the current timezone-aware datetime."""
    now = datetime.utcnow()
    return now.replace(tzinfo=pytz.utc)


def utc_now_serialized() -> str:
    """Return the current datetime, at UTC, serialized.

    :return: String with the ISO format of the current date at UTC.
    """
    now = utc_now()
    return now.isoformat()
