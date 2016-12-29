"""Project Workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState as WS

import logging


logger = logging.getLogger(__name__)


class ProjectWorkflow(BriefyWorkflow):
    """Workflow for a Project."""

    entity = 'project'
    initial_state = 'created'

    created = WS(
        'created', 'Created',
        'Project created.'
    )

    ongoing = WS(
        'ongoing', 'On Going',
        'On Going.'
    )

    completed = WS(
        'completed', 'Completed',
        'Completed.'
    )

    # Transitions:
    @created.transition(ongoing, 'can_start')
    @completed.transition(ongoing, 'can_start')
    def start(self):
        """Start a project, moving it to On Going."""
        pass

    @ongoing.transition(completed, 'can_close')
    def close(self):
        """Close a project, moving it to Completed."""
        pass

    @Permission(groups=[G['bizdev'], G['system']])
    def can_start(self):
        """Validate if user can start this project."""
        return True

    @Permission(groups=[G['bizdev'], G['system']])
    def can_close(self):
        """Validate if user can close this project."""
        return True
