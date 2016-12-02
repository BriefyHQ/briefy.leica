"""Asset Workflow."""
from briefy.common.vocabularies.roles import Groups as G
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState as WS

import logging


logger = logging.getLogger(__name__)


class AssetWorkflow(BriefyWorkflow):
    """Workflow for an Asset."""

    entity = 'asset'
    initial_state = 'created'

    # States:
    created = WS('created', 'Created')
    """State: Asset created."""

    edit = WS('edit', 'Edit')
    """State: Request asset edit."""

    deleted = WS('deleted', 'Deleted')
    """State: Asset is deleted."""

    validation = WS('validation', 'In Validation')
    """State: Under machine validation."""

    discarded = WS('discarded', 'Discarded')
    """State: Asset was discarded."""

    pending = WS('pending', 'Pending Approval')
    """State: Under QA validation."""

    reserved = WS('reserved', 'Reserved')
    """State: Reserved for future use."""

    post_processing = WS('post_processing', 'Post Processing')
    """State: Asset under manual post-processing"""

    approved = WS('approved', 'Approved')
    """State: Ready for delivery."""

    refused = WS('refused', 'Refused')
    """State: Customer refused the asset."""

    # Transitions:
    @created.transition(validation, 'can_submit')
    @edit.transition(validation, 'can_submit')
    def submit(self):
        """Transition: After asset creation, or edition submit it to machine validation.

        Permission: :func:`AssetWorkflow.can_submit`
        """
        # Update metadata on the object
        asset = self.document
        asset.update_metadata()

    @validation.transition(edit, 'can_validate')
    def invalidate(self):
        """Transition: Invalidate an asset and send it to edition.

        Permission: :func:`AssetWorkflow.can_validate`
        """
        pass

    @validation.transition(pending, 'can_validate')
    @edit.transition(pending, 'can_validate')
    def validate(self):
        """Transition: Validate an asset and send it to pending.

        Permission: :func:`AssetWorkflow.can_validate`
        """
        pass

    @pending.transition(edit, 'can_approve')
    def request_edit(self):
        """Tramsition: Request an edit on the asset.

        Permission: :func:`AssetWorkflow.can_approve`
        """
        pass

    @pending.transition(deleted, 'can_delete')
    @edit.transition(deleted, 'can_delete')
    def delete(self):
        """Tramsition: Delete the asset.

        Permission: :func:`AssetWorkflow.can_delete`
        """
        pass

    @pending.transition(discarded, 'can_discard')
    def discard(self):
        """Transition: Discard the asset.

        Permission: :func:`AssetWorkflow.can_discard`
        """
        pass

    @pending.transition(post_processing, 'can_process')
    def process(self):
        """Transition: Move asset to post processing.

        Permission: :func:`AssetWorkflow.can_process`
        """
        pass

    @pending.transition(reserved, 'can_reserve')
    @approved.transition(reserved, 'can_reserve')
    def reserve(self):
        """Transition: Reserve an asset.

        Permission: :func:`AssetWorkflow.can_reserve`
        """
        pass

    @pending.transition(approved, 'can_approve')
    @reserved.transition(approved, 'can_approve')
    def approve(self):
        """Transition: Approve an asset.

        Permission: :func:`AssetWorkflow.can_approve`
        """
        pass

    @approved.transition(refused, 'can_reject')
    def refuse(self):
        """Transition: Customer refused an asset.

        Permission: :func:`AssetWorkflow.can_reject`
        """
        pass

    @discarded.transition(pending, 'can_discard')
    @post_processing.transition(pending, 'can_process')
    @reserved.transition(pending, 'can_reserve')
    @refused.transition(pending, 'can_reserve')
    def retract(self):
        """Transition: Send an asset back to pending.

        Permission: :func:`AssetWorkflow.can_reserve`
        """
        pass

    @Permission(groups=[G['system'], G['professionals'], G['qa']])
    def can_submit(self):
        """Permission: Validate if user can submit the asset to validation.

        Groups: g:system, g:professionals, g:qa
        """
        return True

    @Permission(groups=[G['system'], ])
    def can_validate(self):
        """Permission: Validate if user can validade/invalidate an asset.

        Groups: g:system
        """
        return True

    @Permission(groups=[G['qa'], ])
    def can_discard(self):
        """Permission: Validate if user can discard an asset."""
        return True

    @Permission(groups=[G['qa'], ])
    def can_reserve(self):
        """Permission: Validate if user can reserve an asset."""
        return True

    @Permission(groups=[G['qa'], ])
    def can_approve(self):
        """Permission: Validate if user can approve an asset."""
        return True

    @Permission(groups=[G['qa'], ])
    def can_retract(self):
        """Permission: Validate if user can retract an asset."""
        return True

    @Permission(groups=[G['qa'], ])
    def can_process(self):
        """Permission: Validate if user can mark an asset to processed."""
        return True

    @Permission(groups=[G['customers'], ])
    def can_reject(self):
        """Permission: Validate if user can reject an asset."""
        return True

    @Permission(groups=[G['professionals'], ])
    def can_delete(self):
        """Permission: Validate if professional can delete this asset."""
        allowed_job_status = ['awaiting_assets', ]
        obj = self.document
        job = obj.job
        if job and job.state in allowed_job_status:
            return True
        return False
