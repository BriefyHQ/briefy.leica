"""Event subscribers for briefy.leica.models.asset.Asset."""
from briefy.common.users import SystemUser
from briefy.leica.events.asset import AssetCreatedEvent
from briefy.leica.events.asset import AssetUpdatedEvent
from briefy.leica.subscribers import safe_update_metadata
from briefy.leica.subscribers import safe_workflow_trigger_transitions
from briefy.leica.utils import s3
from pyramid.events import subscriber


@subscriber(AssetCreatedEvent)
def asset_created_handler(event):
    """Handle asset created event."""
    obj = event.obj
    source_path = obj.source_path
    s3.move_asset_source_file(source_path)
    transitions = [('submit', ''), ]
    safe_workflow_trigger_transitions(event, transitions=transitions)


@subscriber(AssetUpdatedEvent)
def asset_updated_handler(event):
    """Handle asset updated event."""
    obj = event.obj
    last_version = obj.versions[-1]
    changeset = last_version.changeset
    if 'source_path' in changeset:
        source_path = obj.source_path
        s3.move_asset_source_file(source_path)
    safe_update_metadata(obj)


def asset_submit_handler(event):
    """Handle asset submitted event."""
    if event.event_name != 'asset.workflow.submit':
        return
    obj = event.obj
    transitions = []
    # Impersonate the System here
    event.user = SystemUser
    if obj.is_valid:
        transitions.append(
            ('validate', 'Machine check approved')
        )
    else:
        error_message = '\n'.join([c['text'] for c in obj.check_requirements])
        transitions.append(
            ('invalidate', error_message)
        )
    safe_workflow_trigger_transitions(event, transitions=transitions, state='validation')
