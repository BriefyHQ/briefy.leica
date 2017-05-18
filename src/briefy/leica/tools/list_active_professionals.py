"""Dumps all professionals and their last updated photos on a CSV file."""
from briefy.leica.models import Professional

import csv
import datetime
import pytz


mindate = datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC)


def get_date(p):
    """Retrieve the last photo update for a given professional.

    If assignments are associated with the professional, returns blank
    if no last_update_date is set, returns proper message.
    The assignment status is also included.

    """
    assignments = list(p.assignments)
    if not assignments:
        return ''
    assignments.sort(key=lambda a: a.last_submission_date or mindate)
    last_assignment = assignments[-1]
    if not last_assignment.last_submission_date:
        date = 'No assets date'
    else:
        date = last_assignment.last_submission_date.strftime('%Y-%m-%d')
    return ' - '.join((date, last_assignment.state))


def get_data(professionals):
    """Get all professional data in the report order."""
    data = [( p.first_name, p.last_name, p.email, p.main_location.formatted_address if p.main_location else '-', p.mobile.international if p.mobile else '', p.state, get_date(p)) for p in professionals]  # noQA
    return data


def main():
    """Do it all."""
    professionals = Professional.query().all()
    # p.first_name, p.last_name, p.email, p.main_location.formatted_address, p.mobile.international if p.mobile else '', p.state # noQA

    headers = 'First Last Email Address Phone Status Last_Assignment_Update'.split()
    data = get_data(professionals)
    with open('professional_data.csv', 'wt') as file_:
        writer = csv.writer(file_)
        writer.writerow(headers)
        writer.writerows(data)
    print('Created file "professional_data.csv" ')


if __name__ == '__main__':
    main()
