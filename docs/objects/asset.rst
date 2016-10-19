Asset
-----

State Machine
+++++++++++++

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
    state refused: Customer refused\nthe Asset.

    [*] --> validation : submit\n(Professional)
    validation --> edit : invalidate\n(System)
    validation --> pending : validate\n(System)
    edit --> pending : validate\n(QA)
    edit --> deleted : delete\n(Professional)
    edit --> validation : submit\n(Professional)
    pending --> deleted : delete\n(Professional)
    pending --> discarded : discard\n(QA)
    discarded --> pending : retract\n(QA)
    approved --> refused : refuse\n(Customer)
    pending --> post_processing : process\n(QA)
    post_processing --> pending : processed\n(QA)
    pending --> reserved : reserve\n(QA)
    approved --> reserved : reserve\n(QA)
    pending --> edit: request_edit\n(QA)
    pending --> approved: approve\n(QA)
    reserved --> approved: approve\n(QA)
    approved --> pending : retract\n(QA)
    reserved --> pending : retract\n(QA)
    refused --> pending : retract\n(QA)

    @enduml
