Workflow
--------

Workflows definitions.

Jobs
++++

.. uml::

    @startuml

    [*] --> created
    created --> pending : submit
    created --> in_qa : workaround
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
