Customer
--------

Inheritance
+++++++++++

Inheritance diagram for the Customer class:

.. inheritance-diagram:: briefy.leica.models.customer.Customer


Attributes
++++++++++

id (uuid)
    Unique identifier using function :func:`uuid.uuid4`.

    From :class:`briefy.common.db.mixins.identifiable.GUID`.

    .. note::
        ``briefy_id`` field on knack.

slug(string)
    Short name.

    Class attribute: _slug

    Property: slug

    From :class:`briefy.common.db.mixins.metadata.BaseMetadata`.

state_history (json)
    History of workflow transitions one instance had.

    Class attribute: _state_history
    Property: state_history
    From :class:`briefy.common.db.mixins.workflow.Workflow`.

created_at (datetime)
    Date time (UTC) of the object creation.

    From :class:`briefy.common.db.mixins.timestamp.Timestamp`.

description (text)
    Long description of the Customer.

    From :class:`briefy.common.db.mixins.metadata.BaseMetadata`.

external_id (string)
    Unique identifier (external) of the instance.

    .. note::
        ``id`` field on knack

state (string)
    Current workflow state of the instance.

    From :class:`briefy.common.db.mixins.workflow.Workflow`.

title (string)
    Customer display name.

    From :class:`briefy.common.db.mixins.metadata.BaseMetadata`.

updated_at (datetime)
    Date time (UTC) of the last change.

    From :class:`briefy.common.db.mixins.timestamp.Timestamp`.

projects (relation)
    List of Project (child) instances related to the Customer.


State Machine
+++++++++++++

.. uml::

    @startuml

    title Customer Workflow

    state created: Inserted on the Database

    [*] --> created

    @enduml


Database model
++++++++++++++
Database diagram for the Customer data model:

.. sadisplay::
    :module: briefy.leica.models.customer
    :alt: Customer data model
    :render: plantuml
