"""This module contains SQLAlchemy helpers and connectivity."""
from briefy.common.db import Base  # noQA
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
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


def persist(session, obj):
    """Persist an object in the database."""
    try:
        session.add(obj)
        session.flush()
    except IntegrityError as exc:
        # 'DETAIL:' is used in psycopg's error messages, and
        # preceeds "good enough"(tm) information
        # about what is wrong with the payload
        if "DETAIL" in exc.args[0]:
            message = exc.args[0].split("DETAIL:")[-1].strip()
        else:
            message = "Conflict error persisting data"
        raise ValueError(message)

    return None
