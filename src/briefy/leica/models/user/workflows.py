"""User profile workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState as WS

from briefy.leica.utils.user import create_rolleiflex_user

import logging


logger = logging.getLogger(__name__)


class UserProfileWorkflow(BriefyWorkflow):
    """Workflow for a User profile."""

    entity = 'userprofile'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Inserted into the database.'
    )

    active = WS(
        'active', 'Active',
        'User profile is active.'
    )

    inactive = WS(
        'inactive', 'Inactive',
        'User profile is inactive.'
    )

    # Transitions:
    @created.transition(active, 'can_activate')
    @inactive.transition(active, 'can_activate')
    def activate(self):
        """Activate the UserProfile."""
        profile = self.document
        if profile.type == 'customeruserprofile':
            groups = ('g:customers', )
        create_rolleiflex_user(self.document, groups=groups)

    @Permission(groups=[G['system'], G['pm'], G['scout'], G['bizdev']])
    def can_activate(self):
        """Validate if user can activate this user profile."""
        return True

    # Transitions:
    @active.transition(inactive, 'can_inactivate')
    def inactivate(self):
        """Inactivate the UserProfile."""
        pass

    @Permission(groups=[G['system'], G['pm'], G['scout'], G['bizdev']])
    def can_inactivate(self):
        """Validate if user can inactivate this user profile."""
        return True
