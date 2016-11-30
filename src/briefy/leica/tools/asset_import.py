from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.asset import import_assets


import csv
import transaction


CSV_NAME = 's3_paths.csv'


def main(session):
    """Handles all the stuff"""
    asset_reader = csv.reader(open(CSV_NAME))
    # Throw away headers:
    next(asset_reader)
    import_assets(session, asset_reader)


if __name__ == '__main__':
    session = configure(Session)
    with transaction.manager:
        main(session)