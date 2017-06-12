"""Common utilities."""

from uuid import UUID


def ensure_uid(id_):
    """Ensure we have an uid instance."""
    return id_ if isinstance(id_, UUID) else UUID(id_)
