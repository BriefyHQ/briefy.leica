"""Base database configuration."""
from briefy.leica import config
from briefy.leica.db import create_engine


def configure(session):
    """Bind session for 'stand alone' DB usage."""
    engine = create_engine(config.DATABASE_URL, pool_recycle=3600)
    session.configure(bind=engine)
    return session
