"""Project Workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.leica.events.project import ProjectUpdatedEvent

import logging


logger = logging.getLogger(__name__)


class ProjectWorkflow(BriefyWorkflow):
    """Workflow for a Project."""

    entity = 'project'
    initial_state = 'created'
    update_event = ProjectUpdatedEvent

    created = WS(
        'created', 'Created',
        'Project created.'
    )

    ongoing = WS(
        'ongoing', 'On Going',
        'On Going.'
    )

    paused = WS(
        'paused', 'Paused',
        'Paused.'
    )

    completed = WS(
        'completed', 'Completed',
        'Completed.'
    )

    # Transitions:
    @created.transition(ongoing, 'can_start')
    @completed.transition(ongoing, 'can_start')
    @paused.transition(ongoing, 'can_start')
    def start(self):
        """Start a project, moving it to On Going."""
        pass

    @ongoing.transition(completed, 'can_close')
    def close(self):
        """Close a project, moving it to Completed."""
        pass

    @ongoing.transition(paused, 'can_pause')
    def pause(self):
        """Pause a project, no new activity should happen here."""
        pass

    @Permission(groups=[G['bizdev'], G['pm'], G['system']])
    def can_start(self):
        """Validate if user can start this project."""
        return True

    @Permission(groups=[G['pm'], G['system']])
    def can_pause(self):
        """Validate if user can pause this project."""
        return True

    @Permission(groups=[G['pm'], G['system']])
    def can_close(self):
        """Validate if user can close this project."""
        return True
