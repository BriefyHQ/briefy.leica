"""Link workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.vocabularies.roles import LocalRolesChoices as LR
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission


class LinkWorkflow(BriefyWorkflow):
    """Workflow for a link."""

    entity = 'link'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Inserted into the database.'
    )

    deleted = WS(
        'deleted', 'Deleted link',
        'Link was deleted from the platform.'
    )

    # Transitions:
    @created.transition(deleted, 'can_delete')
    def delete(self):
        """Delete a link."""
        pass

    @Permission(groups=[LR['owner'], G['scout'], ])
    def can_delete(self):
        """Validate if user can delete this link."""
        return True
