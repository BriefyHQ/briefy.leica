"""Test user utilities."""
from briefy.leica.utils import rolleiflex

import pytest


testdata = [
    False,
    True
]


@pytest.mark.parametrize('authenticate', testdata)
def test__get_headers(authenticate):
    """Test _get_headers function."""
    func = rolleiflex._get_headers
    headers = func(authenticate)

    assert 'x-locale' in headers
    assert 'en_GB' in headers['x-locale']
    assert 'content-type' in headers
    assert 'application/json' in headers['content-type']
    if authenticate:
        assert 'Authorization' in headers
        assert 'JWT ' in headers['Authorization']


def test__get_headers_with_wrong_username():
    """Test _get_headers function when username is not known."""
    func = rolleiflex._get_headers
    username = 'foo@bar.com'
    with pytest.raises(ValueError):
        func(True, username)


testdata = [
    'e2049c55-26b1-4730-b9dc-717f69c49e3a',
]


@pytest.mark.parametrize('profile_id', testdata)
def test_create_user_success(profile_id):
    """Test create_user function with success."""
    from briefy.leica.models import UserProfile

    profile = UserProfile(
        id=profile_id,
        first_name='Foo',
        last_name='Bar',
        email='foo@bar.com',
    )
    initial_password = '123456'
    groups = ['g:briefy', ]

    func = rolleiflex.create_user
    assert func(profile, initial_password, groups)


testdata = [
    '7645fd371-b88d-4700-96a3-4692bb932ccb',
    '8645fd371-b88d-4700-96a3-4692bb932ccb',
    '9645fd371-b88d-4700-96a3-4692bb932ccb',
]


@pytest.mark.parametrize('profile_id', testdata)
def test_create_user_failure(profile_id):
    """Test create_user function with a failure."""
    from briefy.leica.models import UserProfile
    from pyramid.httpexceptions import HTTPBadRequest

    profile = UserProfile(
        id=profile_id,
        first_name='Foo',
        last_name='Bar',
        email='foo@bar.com',
    )
    initial_password = '123456'
    groups = ['g:briefy', ]

    func = rolleiflex.create_user
    with pytest.raises(HTTPBadRequest):
        func(profile, initial_password, groups)
