from briefy.common.utils.transformers import to_serializable
from briefy.leica.models import types


@to_serializable.register(types.CategoryChoices)
def json_jog_category_type(val):
    """CategoryChoices serializer."""
    return str(val.value)


@to_serializable.register(types.ClientJobStatusChoices)
def json_client_job_status(val):
    """ClientJobStatusChoices serializer."""
    return str(val.value)


@to_serializable.register(types.SchedulingIssuesChoices)
def json_scheduling_issues(val):
    """SchedulingIssuesChoices serializer."""
    return str(val.value)
