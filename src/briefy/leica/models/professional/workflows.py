"""Professional workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.vocabularies.roles import LocalRolesChoices as LR
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState as WS


import logging


logger = logging.getLogger(__name__)


class ProfessionalWorkflow(BriefyWorkflow):
    """Workflow for a Professional."""

    entity = 'professional'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Inserted into the database.'
    )

    deleted = WS(
        'deleted', 'Deleted link',
        'Professional was deleted from the platform.'
    )

    # Transitions:
    @created.transition(deleted, 'can_delete')
    def delete(self):
        """Delete a professional."""
        pass

    @Permission(groups=[LR['owner'], G['scout'], ])
    def can_delete(self):
        """Validate if user can delete this professional."""
        return True


class SkillWorkflow(BriefyWorkflow):
    """Workflow for a Skill."""

    entity = 'skill'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Inserted into the database.'
    )

    deleted = WS(
        'deleted', 'Deleted Skill',
        'Professional Skill was deleted from the platform.'
    )

    # Transitions:
    @created.transition(deleted, 'can_delete')
    def delete(self):
        """Delete a professional."""
        pass

    @Permission(groups=[LR['owner'], G['scout'], ])
    def can_delete(self):
        """Validate if user can delete this professional."""
        return True


class LocationWorkflow(BriefyWorkflow):
    """Workflow for a Working Location."""

    entity = 'workinglocation'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Inserted into the database.'
    )

    active = WS(
        'active', 'Active working location',
        'Professional can be hired at this working location.'
    )

    inactive = WS(
        'inactive', 'Inactive working location',
        'Professional cannot be hired at this working location.'
    )

    deleted = WS(
        'deleted', 'Deleted working location',
        'Working location was deleted from the platform.'
    )

    # Transitions:
    @created.transition(active, 'can_submit')
    @inactive.transition(active, 'can_certify')
    def submit(self):
        """Transition a working locaiton from created or inactive to active."""
        pass

    @active.transition(inactive, 'can_inactivate')
    def inactivate(self):
        """Inactivate a working location."""
        pass

    @active.transition(deleted, 'can_delete')
    @inactive.transition(deleted, 'can_delete')
    def delete(self):
        """Delete a working location."""
        pass

    # Permissions:
    @Permission(groups=[G['professionals'], ])
    def can_submit(self):
        """Validate if user can submit a profile."""
        return True

    @Permission(groups=[LR['owner'], G['scout'], ])
    def can_activate(self):
        """Validate if user can activate this working location."""
        return True

    @Permission(groups=[LR['owner'], G['scout'], ])
    def can_inactivate(self):
        """Validate if user can inactivate this working location."""
        return True

    @Permission(groups=[LR['owner'], G['scout'], ])
    def can_delete(self):
        """Validate if user can delete this working location."""
        return True


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
