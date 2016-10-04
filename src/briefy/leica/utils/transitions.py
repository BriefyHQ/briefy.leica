"""Transition helpers for Leica."""


def approve_assets_in_job(job: 'Job', context) -> list:
    """Approve all pending assets in a Job.

    :param job: Internal Briefy Job.
    :param context: Workflow context.
    :returns: List of approved assets in this job.
    """
    all_assets = job.assets
    pending = [
        a for a in all_assets if a.state in ('pending')
    ]
    assets_ids = [a.id for a in all_assets if a.state in ('approved')]
    for asset in pending:
        asset.workflow.context = context
        # Approve asset
        asset.workflow.approve()
        assets_ids.append(asset.id)
    return assets_ids
