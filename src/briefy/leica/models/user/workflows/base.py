"""Base User profile workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.leica.utils.user import activate_or_create_user
from briefy.leica.utils.user import inactivate_user


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
        elif profile.type == 'internaluserprofile':
            groups = ('g:briefy',)
        activate_or_create_user(self.document, groups=groups)

    # Transitions:
    @active.transition(inactive, 'can_inactivate')
    def inactivate(self):
        """Inactivate the UserProfile."""
        inactivate_user(self.document)
        pass

    @Permission(groups=[G['system'], G['pm'], G['scout'], G['bizdev'], G['finance']])
    def can_inactivate(self):
        """Validate if user can inactivate this user profile."""
        return True
