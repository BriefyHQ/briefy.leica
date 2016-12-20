from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.customer import CustomerSync
from briefy.leica.sync.job import JobSync
from briefy.leica.sync.professional import PhotographerSync
from briefy.leica.sync.project import ProjectSync
from briefy.leica.sync.user import update_users
from briefy.leica.tools import logger # noqa

import transaction


def main(session):
    """Import Project script."""
    update_users()
    CustomerSync(session)()
    ProjectSync(session)()
    PhotographerSync(session)()
    JobSync(session)()


if __name__ == '__main__':
    session = configure(Session)
    with transaction.manager:
        main(session)
