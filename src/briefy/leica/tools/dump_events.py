"""Script to list all events triggered by Leica."""
from briefy.leica.models.asset.workflows import AssetWorkflow
from briefy.leica.models.comment.workflows import CommentWorkflow
from briefy.leica.models.customer.workflows import BillingAddressWorkflow
from briefy.leica.models.customer.workflows import ContactWorkflow
from briefy.leica.models.customer.workflows import CustomerWorkflow
from briefy.leica.models.job.workflows import AssignmentWorkflow
from briefy.leica.models.job.workflows import OrderLocationWorkflow
from briefy.leica.models.job.workflows import OrderWorkflow
from briefy.leica.models.job.workflows import PoolWorkflow
from briefy.leica.models.professional.workflows import LinkWorkflow
from briefy.leica.models.professional.workflows import LocationWorkflow
from briefy.leica.models.professional.workflows import ProfessionalWorkflow
from briefy.leica.models.project.workflows import ProjectWorkflow
from briefy.leica.models.user.workflows import BriefyUserProfileWorkflow
from briefy.leica.models.user.workflows import CustomerUserProfileWorkflow


entities = [
    'asset',
    'assignment',
    'briefyuserprofile',
    'comment',
    'customer',
    'customeruserprofile',
    'order',
    'pool',
    'professional',
    'project',
]


ws_events = [
    'created',
    'updated',
]


workflows = [
    AssetWorkflow,
    CommentWorkflow,
    CustomerWorkflow,
    BillingAddressWorkflow,
    ContactWorkflow,
    AssignmentWorkflow,
    OrderLocationWorkflow,
    OrderWorkflow,
    PoolWorkflow,
    ProfessionalWorkflow,
    LocationWorkflow,
    LinkWorkflow,
    ProjectWorkflow,
    BriefyUserProfileWorkflow,
    CustomerUserProfileWorkflow,
]


def _get_workflow_events():
    """List of workflow events."""
    events = []
    for wf in workflows:
        model_name = wf.entity
        states = wf._states_sorted
        for state in states:
            transitions = state._transitions
            for transition in transitions:
                name = '{model_name}.workflow.{transition_name}'.format(
                    model_name=model_name,
                    transition_name=transition
                )
                events.append(name)
    return events


def _get_ws_events():
    """List of workflow events."""
    events = []
    for entity in entities:
        for event in ws_events:
            name = '{model_name}.{event}'.format(
                model_name=entity,
                event=event,
            )
            events.append(name)
    return events


def get_all_events():
    """Return a list of all events."""
    all_events = []
    all_events.extend(_get_workflow_events())
    all_events.extend(_get_ws_events())
    all_events.sort()
    return sorted(list(set(all_events)))


if __name__ == '__main__':
    print(get_all_events())
