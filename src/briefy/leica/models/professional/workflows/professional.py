"""Professional workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.vocabularies.roles import LocalRolesChoices as LR
from briefy.common.workflow import WorkflowState as WS
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.leica.utils.user import activate_or_create_user
from briefy.leica.utils.user import activate_user
from briefy.leica.utils.user import inactivate_user


class ProfessionalWorkflow(BriefyWorkflow):
    """Workflow for a Professional."""

    entity = 'professional'
    initial_state = 'created'

    # States
    created = WS(
        'created', 'Created',
        'Inserted into the database.'
    )

    pending = WS(
        'pending', 'Pending',
        'Waiting for QA Approval.'
    )

    validation = WS(
        'validation', 'Legal checking',
        'Waiting for legal/documents checking.'
    )

    rejected = WS(
        'rejected', 'Rejected',
        'Professional that does not meet the requirements.'
    )

    trial = WS(
        'trial', 'On Trial',
        'Professional that is on trial basis.'
    )

    active = WS(
        'active', 'Active',
        'Professional that is currently working with us.'
    )

    inactive = WS(
        'inactive', 'Inactive',
        'Professional that is not available to be assigned.'
    )

    deleted = WS(
        'deleted', 'Deleted professional',
        'Professional was deleted from the platform.'
    )

    # Transitions:
    @created.transition(deleted, 'can_delete')
    @active.transition(deleted, 'can_delete')
    @inactive.transition(deleted, 'can_delete')
    @trial.transition(deleted, 'can_delete')
    @rejected.transition(deleted, 'can_delete')
    @validation.transition(deleted, 'can_delete')
    @pending.transition(deleted, 'can_delete')
    def delete(self):
        """Delete a professional from our platform."""
        pass

    @created.transition(pending, 'can_submit')
    def submit(self):
        """Submit a Professional for QA Validation."""
        pass

    @pending.transition(rejected, 'can_quality_reject')
    @validation.transition(rejected, 'can_legal_reject')
    def reject(self):
        """Reject a professional application."""
        pass

    @pending.transition(validation, 'can_approve')
    def approve(self):
        """Quality approval of a professional application."""
        groups = ('g:professionals',)
        activate_or_create_user(self.document, groups=groups)

    @validation.transition(trial, 'can_validate')
    def validate(self):
        """Legal validation of a professional application."""
        pass

    @trial.transition(active, 'can_activate')
    @inactive.transition(active, 'can_activate')
    def activate(self):
        """Activate a professional."""
        professional = self.document
        # Activate on Rolleiflex only if current state is inactive.
        if professional.state == 'inactive':
            activate_user(professional)

    @active.transition(inactive, 'can_inactivate')
    @trial.transition(inactive, 'can_inactivate')
    def inactivate(self):
        """Inactivate a professional."""
        inactivate_user(self.document)

    @active.transition(active, 'can_assign', required_fields=('pools_ids',))
    @trial.transition(trial, 'can_assign', required_fields=('pools_ids',))
    def assign(self, **kwargs):
        """Change pools this professional belongs to."""
        from briefy.leica.models import Pool
        fields = kwargs['fields']
        professional = self.document
        pools = []
        pool_ids = fields.get('pools_ids')
        if pool_ids:
            pools = Pool.query().filter(Pool.id.in_(pool_ids)).all()
        professional.pools = pools

    @Permission(groups=[LR['owner'], G['scout'], G['support'], ])
    def can_delete(self):
        """Validate if user can delete this professional."""
        return True

    @Permission(groups=[LR['owner'], G['scout'], G['qa'], G['pm']])
    def can_submit(self):
        """Validate if user can submit this professional for QA approval."""
        return True

    @Permission(groups=[LR['owner'], G['qa'], G['scout'], ])
    def can_quality_reject(self):
        """Validate if user can reject this professional application."""
        return True

    @Permission(groups=[LR['owner'], G['finance'], ])
    def can_legal_reject(self):
        """Validate if user can reject this professional application."""
        return True

    @Permission(groups=[LR['owner'], G['qa'], G['scout']])
    def can_approve(self):
        """Validate if user can approve this professional application."""
        return True

    @Permission(groups=[LR['owner'], G['finance'], ])
    def can_validate(self):
        """Validate if user can validate this professional application."""
        return True

    @Permission(groups=[LR['owner'], G['system'], G['pm'], G['qa'], G['scout']])
    def can_activate(self):
        """Validate if user can activate this professional application."""
        return True

    @Permission(groups=[LR['owner'], G['system'], G['pm'], G['qa'], G['scout']])
    def can_inactivate(self):
        """Validate if user can inactivate this professional application."""
        return True

    @Permission(groups=[G['system'], G['pm'], G['scout']])
    def can_assign(self):
        """Validate if user can assign this professional to a pool."""
        return True
