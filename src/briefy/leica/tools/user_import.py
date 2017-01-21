"""Main script to import user profiles (except professional) from Knack."""
from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.userprofile import CustomerUserProfileSync
from briefy.leica.sync.userprofile import ProjectManagerProfileSync
from briefy.leica.sync.userprofile import QAManagerProfileSync
from briefy.leica.sync.userprofile import ScoutManagerProfileSync
from briefy.leica.sync.userprofile import FinanceManagerProfileSync
from briefy.leica.sync.userprofile import AccountManagerProfileSync
from briefy.leica.sync.userprofile import SupervisorProfileSync
from briefy.leica.sync.user import update_users
from briefy.leica.tools import logger # noqa


def main(session, transaction):
    """Import User profiles script."""
    update_users()
    CustomerUserProfileSync(session, transaction)()
    ProjectManagerProfileSync(session, transaction)()
    QAManagerProfileSync(session, transaction)()
    ScoutManagerProfileSync(session, transaction)()
    FinanceManagerProfileSync(session, transaction)()
    AccountManagerProfileSync(session, transaction)()
    SupervisorProfileSync(session, transaction)()


if __name__ == '__main__':
    session = configure(Session)
    import transaction
    main(session, transaction)
