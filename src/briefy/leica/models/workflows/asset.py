"""Asset Workflow."""
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState
from briefy.leica.models.workflows.utils import G_PROF
from briefy.leica.models.workflows.utils import G_QA
from briefy.leica.models.workflows.utils import G_SYS

import logging


logger = logging.getLogger(__name__)


class AssetWorkflow(BriefyWorkflow):
    """Workflow for an Asset."""

    entity = 'asset'
    initial_state = 'created'

    # States:
    created = WorkflowState('created', description='Asset created')
    edit = WorkflowState('edit', description='Request asset edit')
    validation = WorkflowState(
        'validation', title='In Validation',
        description='Asset under automatic validation')
    rejected = WorkflowState('rejected', title='Rejected', description='Asset Rejected')
    pending = WorkflowState('pending', title='Pending Approval',
                            description='Under verification by internal Q.A.')
    reserved = WorkflowState('reserved', description='Reserved for future use')
    post_processing = WorkflowState('post_processing', title='Post Processing',
                                    description='Asset under manual post-processing')
    approved = WorkflowState('approved', description='Ready for delivery')
    delivered = WorkflowState('delivered', description='Delivered to customer')

    # Transitions:
    submit = created.transition(state_to=validation, permission='can_submit',
                                extra_states=(edit,))
    invalidate = validation.transition(state_to=edit, permission='can_validate',
                                       title='Invalidate')
    validate = validation.transition(state_to=pending, permission='can_validate',
                                     extra_states=(edit,))

    discard = pending.transition(state_to=rejected, permission='can_discard',
                                 extra_states=(delivered,))
    process = pending.transition(state_to=post_processing, permission='can_start_processing')
    reserve = pending.transition(state_to=reserved, permission='can_reserve',
                                 extra_states=(approved,))
    reject = pending.transition(state_to=edit, permission='can_reject')

    approve = pending.transition(state_to=approved, permission='can_approve',
                                 extra_states=(reserved,))
    retract = approved.transition(state_to=pending, permission='can_retract',
                                  extra_states=(rejected, reserved,))
    deliver = approved.transition(state_to=delivered, permission='can_deliver',)
    processed = post_processing.transition(state_to=pending, permission='can_end_processing')

    # Permissions:
    perm_groups = Permission().for_groups
    can_submit = perm_groups(G_PROF, G_QA)
    can_invalidate = perm_groups(G_SYS, G_PROF, G_QA)
    can_discard = perm_groups(G_QA)
    can_reserve = perm_groups(G_QA)
    can_approve = perm_groups(G_QA)
    can_start_processing = perm_groups(G_QA)
    can_reserve = perm_groups(G_QA)
    can_reject = perm_groups(G_QA)
    can_retract = perm_groups(G_QA)
    can_deliver = perm_groups(G_SYS)
    can_end_processing = perm_groups(G_QA)

    @Permission
    def can_validate(self):
        """Logic to check if a user could trigger a validation process."""
        allowed_groups = [G_SYS, G_QA]
        is_right_state = False
        if self.state.name == self.edit.name:
            is_right_state = True
        elif self.state.name == self.validation.name:
            is_right_state = True
            allowed_groups.extend([G_PROF])
        user_has_role = [p for p in allowed_groups if p in self.context.groups]
        return is_right_state and user_has_role
