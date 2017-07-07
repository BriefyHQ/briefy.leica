"""This module contains SQLAlchemy helpers and connectivity."""
from briefy.common.db import Base  # noQA
from briefy.leica import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


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


def db_configure(session):
    """Bind session for 'stand alone' DB usage."""
    engine = create_engine(config.DATABASE_URL, pool_recycle=3600)
    session.configure(bind=engine)
    return session
