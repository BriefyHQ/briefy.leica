"""Customer User profile workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.workflow import Permission
from briefy.leica.models.user.workflows.base import UserProfileWorkflow


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
