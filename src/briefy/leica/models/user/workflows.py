"""User profile workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.leica.utils.user import activate_or_create_user
from briefy.leica.utils.user import inactivate_user

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
        groups = ()
        if profile.type == 'customeruserprofile':
            groups = ('g:customers', )
        elif profile.type == 'briefyuserprofile':
            groups = ('g:briefy',)
        activate_or_create_user(self.document, groups=groups)

    # Transitions:
    @active.transition(inactive, 'can_inactivate')
    def inactivate(self):
        """Inactivate the UserProfile."""
        inactivate_user(self.document)


class CustomerUserProfileWorkflow(UserProfileWorkflow):
    """Workflow for a Customer User profile."""

    entity = 'customeruserprofile'

    @Permission(groups=[G['system'], G['pm'], G['scout'], G['bizdev'], G['finance']])
    def can_activate(self):
        """Validate if user can activate this user profile."""
        return True

    @Permission(groups=[G['system'], G['pm'], G['scout'], G['bizdev'], G['finance']])
    def can_inactivate(self):
        """Validate if user can inactivate this user profile."""
        return True


class BriefyUserProfileWorkflow(UserProfileWorkflow):
    """Workflow for a Briefy user profile."""

    entity = 'briefyuserprofile'

    @Permission(groups=[G['system'], G['support']])
    def can_activate(self):
        """Validate if user can activate this user profile."""
        return True

    @Permission(groups=[G['system'], G['support']])
    def can_inactivate(self):
        """Validate if user can inactivate this user profile."""
        return True
