"""Pool workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission


class PoolWorkflow(BriefyWorkflow):
    """Workflow for a Pool."""

    entity = 'pool'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Pool created.'
    )

    active = WS(
        'active', 'Active',
        'Pool is active.'
    )

    inactive = WS(
        'inactive', 'Inactive',
        'Pool is inactive.'
    )

    @created.transition(active, 'submit')
    def submit(self, **kwargs):
        """Transition: Pool was submitted."""
        pass

    @Permission(groups=[G['scout'], G['pm'], ])
    def can_submit(self):
        """Permission: Validate if user can submit a Pool.

        Groups: g:pm, g:scout
        """
        return True

    @active.transition(inactive, 'can_disable')
    def disable(self, **kwargs):
        """Transition: Pool was moved to inactive."""
        pass

    @Permission(groups=[G['scout'], G['pm'], ])
    def can_disable(self):
        """Permission: Validate if user can inactive a Pool.

        Groups: g:pm, g:scout
        """
        return True

    @inactive.transition(active, 'can_reactivated')
    def reactivated(self, **kwargs):
        """Transition: Pool was moved back to active."""
        pass

    @Permission(groups=[G['scout'], G['pm'], ])
    def can_reactivated(self):
        """Permission: Validate if user can reactivated a Pool.

        Groups: g:pm, g:scout
        """
        return True
