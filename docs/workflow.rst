Workflow
--------

Workflows definitions.

Assets
++++++

.. uml::

    @startuml

    [*] --> created
    created --> validation : submit
    validation --> edit : invalidate
    validation --> pending : validate
    edit --> pending : validate
    edit --> validation : submit
    pending --> discarded : discard
    discarded --> pending : retract
    delivered --> rejected : reject
    pending --> post_processing : process
    post_processing --> pending : processed
    pending --> reserved : reserve
    approved --> reserved : reserve
    pending --> edit: request_edit
    pending --> approved: approve
    reserved --> approved: approve
    approved --> pending : retract
    rejected --> pending : retract
    reserved --> pending : retract
    approved --> delivered : deliver
    delivered --> [*]

    @enduml

Jobs
++++

.. uml::

    @startuml

    [*] --> created
    created --> pending : submit
    pending --> in_qa : workaround_qa
    pending --> awaiting_assets : workaround_upload
    pending --> assigned: assign
    pending --> published: publish
    published --> pending: retract
    published --> scheduled: self_assign
    published : available as "job poll"
    assigned --> scheduled: schedule
    scheduled --> assigned: scheduling_issues
    awaiting_assets --> assigned: schedule_reshoot
    scheduled --> awaiting_assets: ready_for_upload
    awaiting_assets --> in_qa: upload
    in_qa --> awaiting_assets: reject
    in_qa --> approved: approve
    in_qa --> pending: reassign
    approved --> in_qa: retract_approval
    approved --> completed: deliver
    completed --> in_qa: customer_reject
    completed --> [*]

    @enduml
