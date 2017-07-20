"""Test date utilities."""
from briefy.leica.utils import date
from datetime import datetime
from pytz import UTC


def test_utc_now():
    """Test utc_now function."""
    func = date.utc_now

    value = func()
    assert isinstance(value, datetime)
    assert value.tzinfo == UTC


def test_utc_now_serialized():
    """Test utc_now_serialized function."""
    func = date.utc_now_serialized

    value = func()
    assert isinstance(value, str)
    assert value.endswith('+00:00')
