from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.project import ProjectSync
from briefy.leica.tools import logger # noqa


def main(session, transaction):
    """Import Project script."""
    ProjectSync(session, transaction)()


if __name__ == '__main__':
    session = configure(Session)
    import transaction
    main(session, transaction)
