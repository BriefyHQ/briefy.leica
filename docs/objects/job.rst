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
    state refused: Customer refuse\ntemporary
    state perm_refused: Customer refuse\npermanently
    state perm_rejected: QA reject\npermanently

    [*] --> validation : submit\n(Customer, Biz, System)
    validation --> edit : invalidate\n(System)
    edit --> validation : submit\n(Customer, Biz)
    validation --> pending : validate\n(System)
    pending --> assigned: assign\n(Scout)
    pending --> published: publish\n(PM, Customer, Scout, System)
    published --> pending: retract\n(PM, Customer, Scout)
    published --> scheduled: self_assign\n(Professional)
    assigned --> scheduled: schedule\n(Professional, PM)
    assigned --> assigned: scheduling_issues\n(Professional, PM)
    assigned --> pending: unassing\n(PM, Professionals)
    assigned --> published: unassing\n(PM, Professional)
    scheduled --> assigned: scheduling_issues\n(Professional, PM)
    awaiting_assets --> scheduled: schedule\n(Professional)
    awaiting_assets --> approved: approve\n(QA)
    scheduled --> awaiting_assets: ready_for_upload\n(System)
    scheduled --> scheduled: reschedule\n(Professional, PM)
    scheduled --> pending: cancel_schedule\n(Customer, Professional, PM)
    scheduled --> published: back_to_job_pool\n(Customer, Professional, PM)
    awaiting_assets --> in_qa: upload\n(Professional)
    in_qa --> awaiting_assets: refused\n(QA)
    in_qa --> approved: approve\n(QA)
    in_qa --> perm_rejected: perm_reject\nNew job created\n(QA)
    approved --> in_qa: retract_approval\n(QA)
    approved --> completed: complete\n(PM, System, Customer)
    approved --> refused: refuse\n(Customer)
    completed --> completed: deliver\n(System)
    refused --> completed: complete\n(PM, Customer)
    refused --> in_qa: retract_approval\n(PM, QA)
    pending --> cancelled: cancel\n(Customer)
    published --> cancelled: cancel\n(Customer)
    assigned --> cancelled: cancel\n(Customer)
    scheduled --> cancelled: cancel\n(Customer)
    refused --> perm_refused: perm_refuse\n(PM, Biz)
    approved --> perm_refused: perm_refuse\n(PM, Biz)
    completed --> perm_refused: perm_refuse\n(PM, Biz)
    completed --> refused: refuse\n(Customer, PM)

    @enduml

Notes
*****
* State validation:

    * Machine checking for completeness of Job briefing
