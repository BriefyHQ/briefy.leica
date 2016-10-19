from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.job import JobSync

import transaction


def main(session):
    """Import customer script"""
    created, updated = JobSync(session)()
    print(len(created), len(updated))


if __name__ == '__main__':
    session = configure(Session)
    with transaction.manager:
        main(session)
