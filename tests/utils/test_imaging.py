"""Test imaging utilities."""
from briefy.leica.utils import imaging

import pytest


testdata = [
    ('4200x3150', 'eq', True),
    ('800x600', 'eq', False),
    ('4200x3150', 'min', True),
    ('8000x6000', 'min', False),
    ('4200x3150', 'max', True),
    ('800x600', 'max', False),
    ('4200x3150', 'lt', False),
    ('4200x3150', 'gt', False)
]


@pytest.mark.parametrize('value,op,expected', testdata)
def test_dimensions(value, op, expected):
    """Test check dimensions."""
    func = imaging._check_dimensions
    metadata = {
        'dimensions': '4200 x 3150',
    }

    assert func(metadata, value, op) is expected


testdata = [
    (4 / 3, 'eq', True),
    (3 / 4, 'eq', False),
]


@pytest.mark.parametrize('value,op,expected', testdata)
def test_ratio(value, op, expected):
    """Test check ratio."""
    func = imaging._check_ratio
    metadata = {
        'dimensions': '4000 x 3000'
    }

    assert func(metadata, value, op) is expected


testdata = [
    (4194304, 'eq', True),
    (4000000, 'eq', False),
    (4194304, 'min', True),
    (4194304, 'max', True),
    (4000000, 'lt', False),
    (4000000, 'gt', True),
]


@pytest.mark.parametrize('value,op,expected', testdata)
def test_size(value, op, expected):
    """Test check image size."""
    func = imaging._check_size
    metadata = {
        'size': 4194304
    }

    assert func(metadata, value, op) is expected


testdata = [
    ('300', 'eq', True),
    ('72', 'eq', False),
]


@pytest.mark.parametrize('value,op,expected', testdata)
def test_dpi(value, op, expected):
    """Test check dpi."""
    func = imaging._check_dpi
    metadata = {
        'dpi': '300'
    }

    assert func(metadata, value, op) is expected


testdata = [
    ('image/jpeg', 'eq', True),
    (['image/jpeg', 'image/png'], 'in', True),
    ('image/gif', 'eq', False),
]


@pytest.mark.parametrize('value,op,expected', testdata)
def test_mimetype(value, op, expected):
    """Test check mimetype."""
    func = imaging._check_mimetype
    metadata = {
        'mimetype': 'image/jpeg'
    }

    assert func(metadata, value, op) is expected


testdata = [
    (
        {
            'dimensions': [{'value': '4200x3150', 'operator': 'eq'}, ],
            'dpi': [{'value': '300', 'operator': 'eq'}, ],
            'ratio': [{'value': 4 / 3, 'operator': 'eq'}, ],
            'mimetype': [{'value': 'image/jpeg', 'operator': 'eq'}, ],
        },
        0
    ),
    (
        {
            'dimensions': [{'value': '4200x3150', 'operator': 'eq'}, ],
            'dpi': [{'value': '300', 'operator': 'eq'}, ],
            'ratio': [{'value': 4 / 3, 'operator': 'eq'}, ],
            'mimetype': [{'value': 'image/tiff', 'operator': 'eq'}, ],
        },
        1
    ),
]


@pytest.mark.parametrize('value,expected', testdata)
def test_check_image_constraints(value, expected):
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

    assert len(func(metadata, value)) == expected
