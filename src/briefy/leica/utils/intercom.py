"""User functions for Intercom integration."""
from briefy.leica import models as m  # noQA
from briefy.leica.config import INTERCOM_APP_ID
from briefy.leica.config import INTERCOM_HASH_KEY
from briefy.leica.models.mixins import get_public_user_info

import hashlib
import hmac
import typing as t


def _generate_hash(message: str) -> str:
    """Given a message, return a hash.

    :param message: String to be hashed
    :return: Hash of the message
    """
    encoding = 'utf-8'
    key = bytes(INTERCOM_HASH_KEY, encoding)
    message = bytes(message, encoding)
    return hmac.new(
        key,
        message,
        digestmod=hashlib.sha256
    ).hexdigest()


def user_hash_from_email(email: str) -> str:
    """Given an email, return an acceptable user_hash to be used with Intercom.

    :param email: User email, will be the key to integrate with Intercom.io
    :return: User hash
    """
    return _generate_hash(email)


def user_hash_from_user_id(user_id: str) -> str:
    """Given an user_id, return an acceptable user_hash to be used with Intercom.

    :param email: User id, will be the key to integrate with Intercom.io
    :return: User hash
    """
    return _generate_hash(user_id)


def get_projects_for_professional(professional: 'm.Professional') -> t.Sequence['m.Project']:
    """Get projects for a professional."""
    assignments = professional.assignments
    projects = tuple({a.project for a in assignments})
    return projects


def get_project_managers(projects: t.Sequence['m.Project']) -> t.Sequence[dict]:
    """Get project managers."""
    project_managers = []
    project_managers_ids = set()
    for project in projects:
        for pm in project.internal_pm:
            if pm not in project_managers_ids:
                project_managers_ids.add(pm)
                project_managers.append(get_public_user_info(str(pm)))
    return project_managers


def intercom_payload_professional(professional: 'm.Professional') -> dict:
    """Return the intercom payload for a professional."""
    # Priority is to old external id info (Knack id)
    old_id = professional.external_id
    user_id = old_id if old_id else str(professional.id)
    email = professional.email
    name = professional.title
    user_hash = user_hash_from_user_id(user_id)
    projects = get_projects_for_professional(professional)
    project_managers = get_project_managers(projects)
    return dict(
        app_id=INTERCOM_APP_ID,
        user_id=user_id,
        email=email,
        created_at=professional.created_at,
        name=name,
        user_hash=user_hash,
        project_managers=[p['fullname'] for p in project_managers],
        projects=[p.title for p in projects]
    )
