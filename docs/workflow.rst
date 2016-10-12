Workflow
--------

Workflows definitions.

Job
+++

State Machine
*************

.. uml::

    @startuml

    title Job Workflow

    state validation: Validate Job\ninformation
    state edit: Customer needs to\nupdate info
    state pending: Waiting for an action
    state published: Available as "job poll"
    state assigned: Professional\is assigned
    state scheduled: Scheduled date
    state cancelled: Cancelled by\n the customer
    state awaiting_assets: Past scheduled\date, waiting for assets.
    state in_qa: Briefy QA
    state approved: Approved by Briefy
    state completed: Waiting for delivery\npackage creation
    state delivered: Delivered to\ncustomer
    state customer_rejected: Customer rejected
    state customer_approved: Customer approved

    [*] --> validation : submit\n(Customer)
    validation --> edit : invalidate\n(System,Biz)
    edit --> validation : submit\n(Customer)
    validation --> pending : validate\n(System,Biz)
    pending --> in_qa : workaround_qa\n(PM, QA)
    pending --> awaiting_assets : workaround_upload\n(PM, QA)
    pending --> assigned: assign\n(Scout)
    pending --> published: publish\n(PM, Customer)
    published --> pending: retract\n(PM, Customer)
    published --> scheduled: self_assign\n(Professional)
    assigned --> scheduled: schedule\n(Professional)
    assigned --> assigned: scheduling_issues\n(Professional)
    scheduled --> assigned: scheduling_issues\n(Professional)
    awaiting_assets --> scheduled: schedule\n(Professional)
    scheduled --> awaiting_assets: ready_for_upload\n(System)
    awaiting_assets --> in_qa: upload\n(Professional)
    in_qa --> awaiting_assets: reject\n(QA)
    in_qa --> approved: approve\n(QA)
    in_qa --> pending: reassign\n(QA)
    approved --> in_qa: retract_approval\n(QA)
    approved --> completed: complete\n(QA, System)
    completed --> delivered: deliver\n(System)
    delivered --> customer_rejected: customer_reject\n(Customer)
    delivered --> customer_approved: customer_approve\n(Customer)
    customer_rejected --> customer_approved: customer_approve\n(Customer, PM)
    customer_rejected --> in_qa: customer_reject\n(PM)
    pending --> cancelled: cancel\n(Customer)
    published --> cancelled: cancel\n(Customer)
    assigned --> cancelled: cancel\n(Customer)
    scheduled --> cancelled: cancel\n(Customer)

    @enduml

Notes
*****
* State validation:

    * Machine checking for completeness of Job briefing

* State awaiting_assets:



Asset
+++++

State Machine
*************
.. uml::

    @startuml

    title Asset Workflow

    state validation: Under machine\nvalidation
    state edit: Professional needs to\nwork on the Asset
    state deleted: Professional deletes\nan Asset
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
    edit --> deleted : delete\n(Professional)
    edit --> validation : submit\n(Professional)
    pending --> deleted : delete\n(Professional)
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
    rejected --> pending : retract\n(QA, PM, Customer)
    reserved --> pending : retract\n(QA)
    approved --> delivered : deliver\n(QA)

    @enduml

