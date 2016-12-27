from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.customer import CustomerSync
from briefy.leica.tools import logger # noqa


def main(session, trasaction):
    """Import Customer script."""
    CustomerSync(session, transaction)()


if __name__ == '__main__':
    session = configure(Session)
    import transaction
    main(session, transaction)
