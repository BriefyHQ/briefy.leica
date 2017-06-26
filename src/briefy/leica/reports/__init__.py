"""Leica Reports package."""
from briefy.leica.utils.transitions import get_transition_date_from_history
from datetime import datetime
from dateutil import parser
from decimal import Decimal
from io import StringIO
from typing import Sequence

import csv


DATETIME_EXPORT = '%Y-%m-%d %H:%M:%S'
DATETIME_TRANSFORM01 = '%Y-%m-%dT%H:%M:%S'
DATETIME_TRANSFORM02 = '%Y-%m-%dT%H:%M:%S.%f'


def export_date_from_history(
        state_history: list,
        transitions: tuple = (),
        first: bool = False
) -> datetime:
    """Convert workflow dates in str format to datetime."""
    date = get_transition_date_from_history(transitions, state_history, first=first)
    date = parser.parse(date) if date else None
    return date


def export_datetime(date: datetime) -> str:
    """Format datetime to csv export."""
    return date.strftime(DATETIME_EXPORT) if date else None


def export_money_to_fixed_point(value: int) -> Decimal:
    """Convert integer representation of money, in cents, to decimal."""
    return Decimal(value) / Decimal(100) if value else None


def export_location(location: object) -> tuple:
    """Extract location data from location object."""
    street = ''
    locality = ''
    country = ''
    if location:
        street = location.info.get('route')
        locality = location.locality
        country = location.country.code

    return street, locality, country


def save_data_to_file(buffer: StringIO, filename: str) -> bool:
    """Save the contents of a StringIO buffer to a real file."""
    with open(filename, 'w') as fout:
        buffer.seek(0)
        fout.write(buffer.read())
    return True


def records_to_csv(records: Sequence, fieldnames: Sequence) -> StringIO:
    """Return a CSV buffer containing all records."""
    fout = StringIO()
    writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    for data in records:
        data = {k: v for k, v in data.items() if k in fieldnames}
        writer.writerow(data)
    return fout
