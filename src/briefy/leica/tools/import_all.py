"""Main script to import all content from Knack."""
from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.customer import CustomerSync
from briefy.leica.sync.job import JobSync
from briefy.leica.sync.professional import PhotographerSync
from briefy.leica.sync.pool import PoolSync
from briefy.leica.sync.project import ProjectSync
from briefy.leica.sync.user import update_users
from briefy.leica.tools import logger # noqa


def main(session, transaction):
    """Import Project script."""
    update_users()
    CustomerSync(session, transaction)()
    ProjectSync(session, transaction)()
    PhotographerSync(session, transaction)()
    PoolSync(session, transaction)()
    JobSync(session, transaction)()


if __name__ == '__main__':
    session = configure(Session)
    import transaction
    main(session, transaction)
