"""Main script to import Jobs."""
from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.job import JobSync

from briefy.leica.tools import logger # noqa


def main(session, transaction, limit=None):
    """Import Job script."""
    JobSync(session, transaction)(limit=limit)


if __name__ == '__main__':
    import transaction
    import sys

    limit = int(sys.argv[1]) if len(sys.argv) >= 2 else None
    session = configure(Session)
    main(session, transaction, limit)
