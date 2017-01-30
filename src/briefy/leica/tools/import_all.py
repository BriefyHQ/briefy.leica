"""Main script to import all content from Knack."""
from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.customer import CustomerSync
from briefy.leica.sync.job import JobSync
from briefy.leica.sync.professional import PhotographerSync
from briefy.leica.sync.pool import PoolSync
from briefy.leica.sync.project import ProjectSync
from briefy.leica.sync.user import update_users
from briefy.leica.sync.userprofile import CustomerUserProfileSync
from briefy.leica.sync.userprofile import ProjectManagerProfileSync
from briefy.leica.sync.userprofile import QAManagerProfileSync
from briefy.leica.sync.userprofile import ScoutManagerProfileSync
from briefy.leica.sync.userprofile import FinanceManagerProfileSync
from briefy.leica.sync.userprofile import AccountManagerProfileSync
from briefy.leica.sync.userprofile import SupervisorProfileSync
from briefy.leica.tools import logger # noqa


def main(session, transaction):
    """Import all data from knack script."""
    update_users()
    CustomerSync(session, transaction)()
    ProjectSync(session, transaction)()
    PoolSync(session, transaction)()
    PhotographerSync(session, transaction)()
    CustomerUserProfileSync(session, transaction)()
    ProjectManagerProfileSync(session, transaction)()
    QAManagerProfileSync(session, transaction)()
    ScoutManagerProfileSync(session, transaction)()
    FinanceManagerProfileSync(session, transaction)()
    AccountManagerProfileSync(session, transaction)()
    SupervisorProfileSync(session, transaction)()
    JobSync(session, transaction)()


if __name__ == '__main__':
    session = configure(Session)
    import transaction
    main(session, transaction)
