"""This module contains SQLAlchemy helpers and connectivity."""
from briefy.common.db import Base  # noQA
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy_continuum import make_versioned
from zope.sqlalchemy import ZopeTransactionExtension


Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

# As our users are not in here, it is not easy to keep track
# of changes using this
make_versioned(user_cls=None)


def get_db(request):
    """Return a valid DB session for the request."""
    return request.registry['db_session_factory']()

# If needed: tweaks to make new objects remains avialble in views after being commited -
# from http://stackoverflow.com/questions/16152241


def get_engine(settings):
    """Return a SQLAlchemy database engine.

    :param settings: App settings
    :type settings: dict
    :returns: A SQLAlchemy database engine
    :rtype: sqlalchemy.engine.base.Engine
    """
    engine = create_engine(settings['sqlalchemy.url'], pool_recycle=3600)
    return engine
