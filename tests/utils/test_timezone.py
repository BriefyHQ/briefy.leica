"""Test Timezone function."""
from briefy.leica.utils import timezone


def test_get_timezone_id_from_coordinates():
    """Test timezone_from_coordinates."""
    func = timezone.timezone_from_coordinates
    lat, lng = (55.6792691, 12.5985028)
    timezone_id = func(lat, lng)
    assert timezone_id == 'Europe/Berlin'


def test_get_timezone_id_fail_bad_user():
    """Test timezone_from_coordinates, failing to get a response."""
    func = timezone.timezone_from_coordinates
    lat, lng = (91.0, 12.5985028)
    timezone_id = func(lat, lng)
    # Error logged
    assert timezone_id is None


def test_get_timezone_id_fail_rate_limit():
    """Test timezone_from_coordinates, failing to get a response."""
    func = timezone.timezone_from_coordinates
    lat, lng = (55.6792691, 181.0)
    timezone_id = func(lat, lng)
    # Error logged
    assert timezone_id is None


def test_get_timezone_id_bad_response():
    """Test timezone_from_coordinates, failing to get a response."""
    func = timezone.timezone_from_coordinates
    lat, lng = (92.0, 182.0)
    timezone_id = func(lat, lng)
    # Error logged
    assert timezone_id is None
