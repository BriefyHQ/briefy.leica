from briefy.common.utils.transformers import to_serializable
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.common.vocabularies.person import GenderCategories
from briefy.leica import vocabularies


@to_serializable.register(CategoryChoices)
def json_job_category_type(val):
    """CategoryChoices serializer."""
    return str(val.value)


@to_serializable.register(GenderCategories)
def json_gender_categories(val):
    """GenderCategories serializer."""
    return str(val.value)


@to_serializable.register(vocabularies.ClientJobStatusChoices)
def json_client_job_status(val):
    """ClientJobStatusChoices serializer."""
    return str(val.value)


@to_serializable.register(vocabularies.SchedulingIssuesChoices)
def json_scheduling_issues(val):
    """SchedulingIssuesChoices serializer."""
    return str(val.value)


@to_serializable.register(vocabularies.JobInputSource)
def json_input_source(val):
    """JobInputSource serializer."""
    return str(val.value)
