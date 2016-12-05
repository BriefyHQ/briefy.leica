Job
---

Inheritance
+++++++++++

Inheritance diagram for the Job class:

.. inheritance-diagram:: briefy.leica.models.job.Job


Attributes
++++++++++

id (uuid)
    Unique identifier using function :func:`uuid.uuid4`.

    From :class:`briefy.common.db.mixins.identifiable.GUID`.

    .. note::
        ``briefy_id`` field on knack.

project_id (uuid)
    Foreign key to :class:`briefy.leica.models.project.Project`.

assignment_date (datetime)
    Date time (UTC) the Job is assigned to a professional.

    Class attribute: _assignment_date

    Property: assignment_date

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

category (string)
    Category describing the Job type.

    List of possible categories from vocabulary
    :class:`briefy.common.vocabularies.categories.CategoryChoices`.

created_at (datetime)
    Date time (UTC) of the object creation.

    From :class:`briefy.common.db.mixins.timestamp.Timestamp`.

customer_job_id (string)
    External identifier of the Job on the customer database.

    .. note::
        ``job_id`` field on knack.

description (text)
    Long description of the Job.

    From :class:`briefy.common.db.mixins.metadata.BaseMetadata`.

external_id (string)
    Unique identifier (external) of the instance.

    .. note::
        ``id`` field on knack.

job_id (string)
    Another legacy (internal) job identifier from knack.

    .. note::
        ``internal_job_id`` field on knack.

job_requirements (text)
    Detailed description of requirements for the Job.

    .. note::
        ``client_specific_requirement`` field on knack.

number_of_photos (integer)
    Number of photos the Professional should provide to deliver the Job.

    .. note::
        ``number_of_photos`` field on knack.

professional_id (uuid)
    UUID identifier of the professional user assigned to the Job.
    This id comes from the instance of :class:`briefy.rolleiflex.models.user.User`.

    .. note::
        ``responsible_photographer`` field on knack.

scheduled_datetime (datetime)
    Date time (local timezone of the job location) scheduled for the Job.

    .. note::
        ``scheduled_shoot_date_time`` field on knack.

state (string)
    Current workflow state of the instance.

    From :class:`briefy.common.db.mixins.workflow.Workflow`.

title (string)
    Job display name.

    From :class:`briefy.common.db.mixins.metadata.BaseMetadata`.

updated_at (datetime)
    Date time (UTC) of the last change.

    From :class:`briefy.common.db.mixins.timestamp.Timestamp`.

assets (relation)
    List of Asset (child) instances related to the Job.

comments (relation)
    List of comments associated with the Job instance.

job_locations(relation)
    List of job locations associated with the Job instance.

project (relation)
    Reference to the Project (parent) instance.


State Machine
+++++++++++++

.. uml::

    @startuml

    title Job Workflow

    state created: Inserted on the Database
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

    [*] --> created
    created --> validation : submit\n(Customer, Biz, System)
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


Database model
++++++++++++++
Database diagram for the Job data model:

.. sadisplay::
    :module: briefy.leica.models.job
    :alt: Job data model
    :render: graphviz