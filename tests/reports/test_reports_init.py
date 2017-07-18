"""Test imaging utilities."""
from briefy.leica.reports import export_asset_types
from briefy.leica.reports import export_date_from_history
from briefy.leica.reports import export_datetime
from briefy.leica.reports import export_location
from briefy.leica.reports import export_money_to_fixed_point
from briefy.leica.reports import records_to_csv
from datetime import datetime
from pytz import utc

import pytest


testdata = [
    (('submit', ), True, datetime(2016, 9, 16, 0, 0, 0, tzinfo=utc)),
    (('refuse', ), True, datetime(2017, 6, 1, 6, 41, 17, 326818, tzinfo=utc)),
    (('refuse', 'deliver', ), True, datetime(2017, 5, 31, 16, 33, 10, 813737, tzinfo=utc)),
]


@pytest.mark.parametrize('transitions,first,expected', testdata)
def test_export_date_from_history(transitions, first, expected):
    """Test export_date_from_history."""
    func = export_date_from_history
    history = [
        {
            'actor': '3966051e-6bfd-4998-9d96-432ddc93d8e9',
            'date': '2016-09-16T00:00:00+00:00',
            'from': '',
            'message': 'Created by Agoda Bangkok on Knack database',
            'to': 'created',
            'transition': ''
        },
        {
            'actor': '3966051e-6bfd-4998-9d96-432ddc93d8e9',
            'date': '2016-09-16T00:00:00+00:00',
            'from': 'created',
            'message': 'Automatic transition to received',
            'to': 'received',
            'transition': 'submit'
        },
        {
            'actor': '414ff864-b9d3-4d75-a355-0a255bb253bf',
            'date': '2016-10-13T08:56:00+00:00',
            'from': 'received',
            'message': 'Photographer assigned',
            'to': 'assigned',
            'transition': 'assign'
        },
        {
            'actor': '899607a7-c69b-44d7-bc54-72651b12af55',
            'date': '2016-10-27T14:00:00+00:00',
            'from': 'assigned',
            'message': 'Scheduled',
            'to': 'scheduled',
            'transition': 'schedule'
        },
        {
            'actor': '899607a7-c69b-44d7-bc54-72651b12af55',
            'date': '2017-01-06T06:40:00+00:00',
            'from': 'scheduled',
            'message': 'Submited',
            'to': 'in_qa',
            'transition': 'start_qa'
        },
        {
            'actor': 'be319e15-d256-4587-a871-c3476affa309',
            'date': '2017-05-31T16:33:10.813737+00:00',
            'from': 'in_qa',
            'message': 'Assets automatic delivered.',
            'to': 'delivered',
            'transition': 'deliver'
        },
        {
            'actor': '75db786e-b29a-4a1d-b77a-3c72a30940d1',
            'date': '2017-06-01T06:41:17.326818+00:00',
            'from': 'delivered',
            'message': '',
            'to': 'refused',
            'transition': 'refuse'
        }
    ]
    assert func(state_history=history, transitions=transitions, first=first) == expected


testdata = [
    (datetime(2012, 3, 29, 12, 0, 0), '2012-03-29 12:00:00'),
    (datetime(2016, 9, 1, 12, 0, 0, tzinfo=utc), '2016-09-01 12:00:00'),
    (datetime(2017, 2, 13, 5, 0, 30, tzinfo=utc), '2017-02-13 05:00:30'),
]


@pytest.mark.parametrize('value,expected', testdata)
def test_export_datetime(value, expected):
    """Test export_datetime."""
    func = export_datetime

    assert func(date=value) == expected


testdata = [
    (10, '0.10'),
    (10000, '100.00'),
    (15050, '150.50'),
]


@pytest.mark.parametrize('value,expected', testdata)
def test_export_money_to_fixed_point(value, expected):
    """Test export_money_to_fixed_point."""
    from decimal import Decimal

    func = export_money_to_fixed_point

    assert func(value) == Decimal(expected)


def test_export_location_empty():
    """Test export_location without a valid location."""
    func = export_location

    assert func(None) == ('', '', '')


def test_export_location():
    """Test export_location."""
    func = export_location

    class DummyLocation:
        """Dummy Location."""

        info = {'route': 'Street name 31', 'locality': 'City', 'country': 'DE'}
        locality = 'City'

        @property
        def country(self) -> object:
            """Return Country object.

            :return: Country object.
            """
            class DummyCountry:
                """Dummy Country."""

                code = 'DE'
                name = 'Germany'

            return DummyCountry()

    location = DummyLocation()

    assert func(location) == ('Street name 31', 'City', 'DE')


def test_records_to_csv():
    """Test records_to_csv."""
    from io import StringIO

    func = records_to_csv
    records = [
        {'code': 'BR', 'title': 'Brazil', 'tld': 'br', 'phone': '55'},
        {'code': 'DE', 'title': 'Germany', 'tld': 'de', 'phone': '49'},
    ]
    fieldnames = ['phone', 'title', 'tld']

    result = func(records=records, fieldnames=fieldnames)
    assert isinstance(result, StringIO)

    result.seek(0)
    lines = result.readlines()
    assert len(lines) == 3
    assert lines[0] == 'phone\ttitle\ttld\r\n'
    assert lines[1] == '55\tBrazil\tbr\r\n'
    assert lines[2] == '49\tGermany\tde\r\n'


testdata = [
    (['Image'], 'Photograph'),
    (['Image', 'ImageRaw'], 'Photograph, Photograph (RAW)'),
    (['Matterport', 'ImageRaw'], '3D Scan, Photograph (RAW)'),
    (['Image360', 'Video'], '360 degree Photograph, Video'),
]


@pytest.mark.parametrize('value,expected', testdata)
def test_export_asset_types(value, expected):
    """Test export_asset_types."""
    func = export_asset_types

    assert func(asset_types=value) == expected
