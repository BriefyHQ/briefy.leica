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
    created = WS(
        'created',
        'Created',
        'Asset created.'
    )
    edit = WS(
        'edit',
        'Edit',
        'Request asset edit.'
    )
    deleted = WS(
        'deleted',
        'Deleted',
        'Asset is deleted.'
    )
    validation = WS(
        'validation',
        'In Validation',
        'Under machine validation.'
    )
    discarded = WS(
        'discarded',
        'Discarded',
        'Asset was discarded.'
    )
    pending = WS(
        'pending',
        'Pending Approval',
        'Under QA validation.'
    )
    reserved = WS(
        'reserved',
        'Reserved'
        'Reserved for future use.'
    )
    post_processing = WS(
        'post_processing',
        'Post Processing',
        'Asset under manual post-processing'
    )
    approved = WS(
        'approved',
        'Approved',
        'Ready for delivery.'
    )
    refused = WS(
        'refused',
        'Refused'
        'Customer refused the asset.'
    )

    # Transitions:
    @created.transition(validation, 'can_submit')
    @edit.transition(validation, 'can_submit')
    def submit(self):
        """After asset creation, or edition submit it to machine validation."""
        # Update metadata on the object
        asset = self.document
        asset.update_metadata()

    @validation.transition(edit, 'can_validate')
    def invalidate(self):
        """Invalidate an asset and send it to edition."""
        pass

    @validation.transition(pending, 'can_validate')
    @edit.transition(pending, 'can_validate')
    def validate(self):
        """Validate an asset and send it to edition."""
        pass

    @pending.transition(edit, 'can_approve')
    def request_edit(self):
        """Request an edit on the asset."""
        pass

    @pending.transition(deleted, 'can_delete')
    @edit.transition(deleted, 'can_delete')
    def delete(self):
        """Delete the asset."""
        pass

    @pending.transition(discarded, 'can_discard')
    def discard(self):
        """Discard the asset."""
        pass

    @pending.transition(post_processing, 'can_process')
    def process(self):
        """Move asset to post processing."""
        pass

    @pending.transition(reserved, 'can_reserve')
    @approved.transition(reserved, 'can_reserve')
    def reserve(self):
        """Reserve an asset."""
        pass

    @pending.transition(approved, 'can_approve')
    @reserved.transition(approved, 'can_approve')
    def approve(self):
        """Approve an asset."""
        pass

    @approved.transition(refused, 'can_reject')
    def refuse(self):
        """Customer refused an asset."""
        pass

    @discarded.transition(pending, 'can_discard')
    @post_processing.transition(pending, 'can_process')
    @reserved.transition(pending, 'can_reserve')
    @refused.transition(pending, 'can_reserve')
    def retract(self):
        """Send an asset back to pending."""
        pass

    @Permission(groups=[G['system'], G['professionals'], G['qa']])
    def can_submit(self):
        """Validate if user can submit the asset to validation."""
        return True

    @Permission(groups=[G['system'], ])
    def can_validate(self):
        """Validate if user can invalidate an asset."""
        return True

    @Permission(groups=[G['qa'], ])
    def can_discard(self):
        """Validate if user can discard an asset."""
        return True

    @Permission(groups=[G['qa'], ])
    def can_reserve(self):
        """Validate if user can reserve an asset."""
        return True

    @Permission(groups=[G['qa'], ])
    def can_approve(self):
        """Validate if user can approve an asset."""
        return True

    @Permission(groups=[G['qa'], ])
    def can_retract(self):
        """Validate if user can retract an asset."""
        return True

    @Permission(groups=[G['qa'], ])
    def can_process(self):
        """Validate if user can mark an asset to processed."""
        return True

    @Permission(groups=[G['customers'], ])
    def can_reject(self):
        """Validate if user can reject an asset."""
        return True

    @Permission(groups=[G['professionals'], ])
    def can_delete(self):
        """Validate if professional can delete this asset."""
        allowed_job_status = ['awaiting_assets', ]
        obj = self.document
        job = obj.job
        if job and job.state in allowed_job_status:
            return True
        return False
