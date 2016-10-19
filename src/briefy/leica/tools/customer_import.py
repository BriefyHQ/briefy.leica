from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.customer import CustomerSync


import transaction


def main(session):
    """Import customer script"""
    created, updated = CustomerSync(session)()
    print(len(created), len(updated))


if __name__ == '__main__':
    session = configure(Session)
    with transaction.manager:
        main(session)
