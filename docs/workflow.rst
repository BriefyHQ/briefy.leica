Workflow
--------

Workflows definitions.

Job
+++

.. uml::

    @startuml

    [*] --> pending : submit
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


Asset
+++++

.. uml::

    @startuml

    state validation: Under machine\nvalidation
    state edit: Professional needs to\nwork on the Asset
    state pending: Under QA evaluation
    state discarded: Not going\nto be used
    state post_processing: Internal\npost processing
    state approved: Approved by QA
    state reserved: Will not be delivered\nbut is available for Briefy.
    state delivered: Delivered to\nthe customer.
    state rejected: Customer rejected\nthe Asset.

    [*] --> validation : submit\n(Professional)
    validation --> edit : invalidate\n(System)
    validation --> pending : validate\n(System)
    edit --> pending : validate\n(QA)
    edit --> validation : submit\n(QA)
    pending --> discarded : discard\n(QA)
    discarded --> pending : retract\n(QA)
    delivered --> rejected : reject\n(QA)
    pending --> post_processing : process\n(QA)
    post_processing --> pending : processed\n(QA)
    pending --> reserved : reserve\n(QA)
    approved --> reserved : reserve\n(QA)
    pending --> edit: request_edit\n(QA)
    pending --> approved: approve\n(QA)
    reserved --> approved: approve\n(QA)
    approved --> pending : retract\n(QA)
    rejected --> pending : retract\n(Customer)
    reserved --> pending : retract\n(QA)
    approved --> delivered : deliver\n(QA)

    @enduml

