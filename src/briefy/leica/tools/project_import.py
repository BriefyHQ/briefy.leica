from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.customer import CustomerSync
from briefy.leica.sync.project import ProjectSync
from briefy.leica.tools import logger # noqa

import transaction


def main(session):
    """Import Project script."""
    CustomerSync(session)()
    ProjectSync(session)()


if __name__ == '__main__':
    session = configure(Session)
    with transaction.manager:
        main(session)
