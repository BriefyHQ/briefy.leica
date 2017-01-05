"""Main script to import Professionals."""
from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.professional import PhotographerSync
from briefy.leica.tools import logger # noqa


def main(session, transaction, limit=None):
    """Import Project script."""
    PhotographerSync(session, transaction)(limit=limit)


if __name__ == '__main__':
    import transaction
    import sys

    session = configure(Session)

    limit = int(sys.argv[1]) if len(sys.argv) >= 2 else None
    main(session, transaction, limit)
