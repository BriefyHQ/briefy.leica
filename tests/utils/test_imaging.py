"""Test imaging utilities."""
from briefy.leica.utils import imaging


def test_dimensions():
    """Test check dimensions."""
    func = imaging._check_dimensions
    metadata = {
        'dimensions': '4200 x 3150',
    }

    assert func(metadata, '4200x3150', 'eq') is True
    assert func(metadata, '800x600', 'eq') is False
    assert func(metadata, '4200x3150', 'min') is True
    assert func(metadata, '8000x6000', 'min') is False
    assert func(metadata, '4200x3150', 'max') is True
    assert func(metadata, '800x600', 'max') is False
    assert func(metadata, '4200x3150', 'lt') is False
    assert func(metadata, '4200x3150', 'gt') is False


def test_ratio():
    """Test check ratio."""
    func = imaging._check_ratio
    metadata = {
        'ratio': '4/3'
    }

    assert func(metadata, '4/3', 'eq') is True
    assert func(metadata, '3/4', 'eq') is False


def test_size():
    """Test check image size."""
    func = imaging._check_size
    metadata = {
        'size': 4194304
    }

    assert func(metadata, 4194304, 'eq') is True
    assert func(metadata, 4000000, 'eq') is False
    assert func(metadata, 4194304, 'min') is True
    assert func(metadata, 4194304, 'max') is True
    assert func(metadata, 4000000, 'lt') is False
    assert func(metadata, 4000000, 'gt') is True


def test_dpi():
    """Test check dpi."""
    func = imaging._check_dpi
    metadata = {
        'dpi': '300'
    }

    assert func(metadata, '300', 'eq') is True
    assert func(metadata, '72', 'eq') is False


def test_mimetype():
    """Test check mimetype."""
    func = imaging._check_mimetype
    metadata = {
        'mimetype': 'image/jpeg'
    }

    assert func(metadata, 'image/jpeg', 'eq') is True
    assert func(metadata, 'image/gif', 'eq') is False


def test_check_image_constraints():
    """Test check image constraints."""
    func = imaging.check_image_constraints
    metadata = {
        'dimensions': '4200 x 3150',
        'width': 4200,
        'height': 3150,
        'ratio': '4/3',
        'size': 4194304,
        'dpi': '300',
        'mimetype': 'image/jpeg'
    }

    constraints = {
        'dimensions': {'value': '4200x3150', 'operator': 'eq'},
        'dpi': {'value': '300', 'operator': 'eq'},
        'ratio': {'value': '4/3', 'operator': 'eq'},
        'mimetype': {'value': 'image/jpeg', 'operator': 'eq'},
    }

    assert func(metadata, constraints) == []

    constraints['mimetype'] = {'value': 'image/tiff', 'operator': 'eq'}

    assert func(metadata, constraints)[0]['check'] == 'mimetype'
    assert func(metadata, constraints)[0]['text'] == 'Check for mimetype failed'
