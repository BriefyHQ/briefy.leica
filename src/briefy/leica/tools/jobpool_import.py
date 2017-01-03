"""Main script to import Job pools."""
from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.pool import JobPoolSync
from briefy.leica.tools import logger # noqa


def main(session, transaction):
    """Import JobPool script."""
    JobPoolSync(session, transaction)()


if __name__ == '__main__':
    session = configure(Session)
    import transaction
    main(session, transaction)
