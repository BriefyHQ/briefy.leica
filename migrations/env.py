"""Configuration for Alembic scripts."""
from alembic import context
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import ALL_MODELS  # noqa
from prettyconf import config
from sqlalchemy import create_engine


target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config('DATABASE_URL')
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, )  # compare_type=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    url = config('DATABASE_URL')
    engine = create_engine(url, pool_recycle=3600)
    Session.configure(bind=engine)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
