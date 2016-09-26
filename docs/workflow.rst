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
    pending --> rejected : discard
    delivered --> rejected : discard
    pending --> post_processing : process
    post_processing --> pending : processed
    pending --> reserved : reserve
    approved --> reserved : reserve
    pending --> edit: reject
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
    pending --> scheduling: assign
    pending --> published: publish
    published --> pending: retract
    published --> scheduling: self_assign
    published : available as "job poll"
    scheduling --> scheduled: schedule
    scheduled --> scheduling: scheduling_issues
    awaiting_assets --> scheduling: scheduling_issues
    scheduled --> awaiting_assets: ready_for_upload
    awaiting_assets --> in_qa: upload
    in_qa --> awaiting_assets: reject
    in_qa --> approved: approve
    approved --> in_qa: retract_approval
    approved --> revision: deliver
    revision --> in_qa: customer_reject
    revision --> completed: customer_approve
    revision --> cancelled: cancel
    completed --> [*]
    cancelled --> [*]

    @enduml
