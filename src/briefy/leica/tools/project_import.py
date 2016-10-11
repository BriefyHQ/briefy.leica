from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.sync.project import ProjectSync


import transaction


def main(session):
    """Import customer script"""
    created, updated = ProjectSync(session)()
    print(len(created), len(updated))


if __name__ == '__main__':
    session = configure(Session)
    with transaction.manager:
        main(session)
