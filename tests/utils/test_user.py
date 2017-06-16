"""Test user utilities."""
from briefy.leica.utils import user

import pytest
import string


testdata = [
    (6, 'AaAaAa'),
    (6, string.digits),
    (6, string.ascii_uppercase + string.digits),
    (8, 'B$$$b2_'),
    (8, string.digits),
    (8, string.ascii_uppercase + string.digits),
]


@pytest.mark.parametrize('size, chars', testdata)
def test_password_generator(size, chars):
    """Test password generation function."""
    func = user.password_generator
    result = func(size, chars)

    assert len(result) == size
    assert len([c for c in result if c not in chars]) == 0


testdata = [
    '645fd371-b88d-4700-96a3-4692bb932ccb',
    'e2049c55-26b1-4730-b9dc-717f69c49e3a',
]


@pytest.mark.parametrize('profile_id', testdata)
def test_activate_or_create_user(profile_id):
    """Test activate_or_create_user function."""
    from briefy.leica.models import UserProfile

    profile = UserProfile(
        id=profile_id,
        first_name='Foo',
        last_name='Bar',
        email='foo@bar.com',
    )
    groups = ['g:briefy', ]

    func = user.activate_or_create_user
    assert func(profile, groups)


testdata = [
    ('645fd371-b88d-4700-96a3-4692bb932ccb', False),
    ('e2049c55-26b1-4730-b9dc-717f69c49e3a', True)
]


@pytest.mark.parametrize('profile_id,expected', testdata)
def test_activate_user(profile_id, expected):
    """Test activate_user function."""
    from briefy.leica.models import UserProfile

    profile = UserProfile(
        id=profile_id,
        first_name='Foo',
        last_name='Bar',
        email='foo@bar.com',
    )

    func = user.activate_user
    assert func(profile) == expected


testdata = [
    ('645fd371-b88d-4700-96a3-4692bb932ccb', False),
    ('e2049c55-26b1-4730-b9dc-717f69c49e3a', True)
]


@pytest.mark.parametrize('profile_id,expected', testdata)
def test_inactivate_user(profile_id, expected):
    """Test inactivate_user function."""
    from briefy.leica.models import UserProfile

    profile = UserProfile(
        id=profile_id,
        first_name='Foo',
        last_name='Bar',
        email='foo@bar.com',
    )

    func = user.inactivate_user
    assert func(profile) == expected
