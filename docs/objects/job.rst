Job
---

State Machine
+++++++++++++

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
