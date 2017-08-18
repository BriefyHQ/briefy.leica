"""Internal User profile workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.workflow import Permission
from briefy.leica.models.user.workflows.base import UserProfileWorkflow


class InternalUserProfileWorkflow(UserProfileWorkflow):
    """Workflow for a Briefy user profile."""

    entity = 'internaluserprofile'

    @Permission(groups=[G['system'], G['support']])
    def can_activate(self):
        """Validate if user can activate this user profile."""
        return True

    @Permission(groups=[G['system'], G['support']])
    def can_inactivate(self):
        """Validate if user can inactivate this user profile."""
        return True
