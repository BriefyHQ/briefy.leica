Project
-------

Inheritance
+++++++++++
Inheritance diagram for the Project class:

.. inheritance-diagram:: briefy.leica.models.project.Project


Attributes
++++++++++

id (uuid)
    Unique identifier using function :func:`uuid.uuid4`.

    From :class:`briefy.common.db.mixins.identifiable.GUID`.

    .. note::
        ``briefy_id`` field on knack.

customer_id (uuid)
    Foreign key to :class:`briefy.leica.models.customer.Customer`.

finance_manager (uuid)
    UUID identifier of the user with role of Finance Manager.
    This id comes from the instance of :class:`briefy.rolleiflex.models.user.User`.

    Class attribute: _finance_manager

    Property: finance_manager

    From :class:`briefy.common.db.mixins.roles.BriefyRoles`.

project_manager (uuid)
    UUID identifier of the user with role of Project Manager.
    This id comes from the instance of :class:`briefy.rolleiflex.models.user.User`.

    Class attribute: _project_manager

    Property: project_manager

    From :class:`briefy.common.db.mixins.roles.BriefyRoles`.

qa_manager (uuid)
    UUID identifier of the user with role of QA Manager.
    This id comes from the instance of :class:`briefy.rolleiflex.models.user.User`.

    Class attribute: _qa_manager

    Property: qa_manager

    From :class:`briefy.common.db.mixins.roles.BriefyRoles`.

scout_manager (uuid)
    UUID identifier of the user with role of Scout Manager.
    This id comes from the instance of :class:`briefy.rolleiflex.models.user.User`.

    Class attribute: _scout_manager

    Property: scout_manager

    From :class:`briefy.common.db.mixins.roles.BriefyRoles`.

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

brief (text)
    URI linking to the Project brief (external document).

    Managed by type :class:`sqlalchemy_utils.URLType`.

    .. note::
        ``briefing`` field on knack.

created_at (datetime)
    Date time (UTC) of the object creation.

    From :class:`briefy.common.db.mixins.timestamp.Timestamp`.

description (text)
    Long description of the Project.

    From :class:`briefy.common.db.mixins.metadata.BaseMetadata`.

external_id (string)
    Unique identifier (external) of the instance.

    .. note::
        ``id`` field on knack

state (string)
    Current workflow state of the instance.

    From :class:`briefy.common.db.mixins.workflow.Workflow`.


tech_requirements (json)
    JSON data map with global requirements for all Jobs in the Project.

title (string)
    Project display name.

    From :class:`briefy.common.db.mixins.metadata.BaseMetadata`.

updated_at (datetime)
    Date time (UTC) of the last change.

    From :class:`briefy.common.db.mixins.timestamp.Timestamp`.

customer (relation)
    Customer (parent) instance related to the Project.

jobs (relation)
    List of Job (child) instances related to the Project.


State Machine
+++++++++++++

.. uml::

    @startuml

    title Project Workflow

    state created: Inserted on the Database

    [*] --> created

    @enduml


Database model
++++++++++++++

Database diagram for the Project data model:

.. sadisplay::
    :module: briefy.leica.models.project
    :alt: Project data model
    :render: graphviz
