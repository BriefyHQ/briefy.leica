Database
--------

Here you can find details about all data models used in Leica service.

Most data models uses one or more classes as bases from briefy.common.db.mixins.

Asset
+++++

Inheritance diagram for the Asset class:


.. inheritance-diagram:: briefy.leica.models.asset.Asset


Database diagram for the Asset data model:


.. sadisplay::
    :module: briefy.leica.models.asset
    :alt: Asset data model
    :render: plantuml


id (uuid)
    Unique identifier using function :func:`uuid.uuid4`.

    From :class:`briefy.common.db.mixins.identifiable.GUID`.

job_id (uuid)
    Foreign key to :class:`briefy.leica.models.job.Job`.

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

author_id (uuid)
    UUID identifier of the user that authored the Asset.

    This id comes from the instance of :class:`briefy.rolleiflex.models.user.User`.

content_type (string)
    Store the content type of the file uploaded as an Asset instance.

    ex: ``image/jpg``

    From :class:`briefy.common.db.mixins.image.Image`.

created_at (datetime)
    Date time (UTC) of the object creation.

    From :class:`briefy.common.db.mixins.timestamp.Timestamp`.

description (text)
    Long description of the asset.

    From :class:`briefy.common.db.mixins.metadata.BaseMetadata`.

filename (string)
    Orginal file name of the Asset.

    From :class:`briefy.common.db.mixins.image.Image`.

height (integer)
    Asset original height.

    From :class:`briefy.common.db.mixins.image.Image`.

history (text)
    History is an unified list where each entry can refer to:

    * A  new comment by some user (comments are full objects with workflow)
    * A transition on the object workflow
    * An editing operation on the mains asset that results in a new binary, this can be the result of:


      * a new upload that superseeds an earlier version,
      * an internal operation (crop, filter, so on)

owner (string)
    Denormalized string with the name of the OWNER of an asset under copyright law,
    disregarding whether he is a Briefy systems user.

raw_metadata (json)
    All orginal metadata extracted from the Asset.
    If the Asset is an Image this will be all the EXIF extracted data.

    From :class:`briefy.common.db.mixins.image.Image`.

size (integer)
    Original file size in bytes.

    From :class:`briefy.common.db.mixins.image.Image`.

source_path (string)
    Relative path of the Asset file inside the filesystem data store (S3)

    From :class:`briefy.common.db.mixins.image.Image`.

state (string)
    Current workflow state of the Asset instance.

    From :class:`briefy.common.db.mixins.workflow.Workflow`.

title (string)
    Asset title.

    From :class:`briefy.common.db.mixins.metadata.BaseMetadata`.

updated_at (datetime)
    Date time (UTC) of the last change.

    From :class:`briefy.common.db.mixins.timestamp.Timestamp`.

uploaded_by (uuid)
    UUID identifier of the user that uploaded the Asset.


width (integer)
    Asset original width.

    From :class:`briefy.common.db.mixins.image.Image`.

job (relation)
    Pointer to the instance of the parent Job object.

comments (relation)
    List of comments associated with the Asset instance.

versions (relation)
    List of old versions the Asset has.


Comments
++++++++

Inheritance diagram for the Comment class:

.. inheritance-diagram:: briefy.leica.models.comment.Comment


Database diagram for the Comment data model:

.. sadisplay::
    :module: briefy.leica.models.comment
    :alt: Comment data model
    :render: plantuml


id (uuid)
    Unique identifier using function :func:`uuid.uuid4`.

    From :class:`briefy.common.db.mixins.identifiable.GUID`.

in_reply_to (uuid)
    Self reference to parent Comment.

    Foreign key to :class:`briefy.leica.models.comment.Comment`.

state_history (json)
    History of workflow transitions one instance had.

    Class attribute: _state_history

    Property: state_history

    From :class:`briefy.common.db.mixins.workflow.Workflow`.

author_id (uuid)
    UUID identifier of the user that authored the Comment.

    This id is the :class:`briefy.rolleiflex.models.user.User` UUID.

comment_order (integer)
    Number used to order the comment sequence.

content (text)
    Raw text with the body (content) of the comment.

created_at (datetime)
    Date time (UTC) of the object creation.

    From :class:`briefy.common.db.mixins.timestamp.Timestamp`.

entity_id (uuid)
    UUID of the reference record the comment is related to.

entity_type (string)
    Name of the entity type / table referenced by the Comment instance.

state (string)
    Current workflow state of the instance.

    From :class:`briefy.common.db.mixins.workflow.Workflow`.

type (string)
    Identifier of the Comment type (polymorphic field).

updated_at (datetime)
    Date time (UTC) of the last change.

    From :class:`briefy.common.db.mixins.timestamp.Timestamp`.

entity (relation)
    Generic relationship (weak foreign key) using :func:`sqlalchemy_utils.generic_relationship`.


Customer
++++++++

Inheritance diagram for the Customer class:

.. inheritance-diagram:: briefy.leica.models.customer.Customer


Database diagram for the Customer data model:

.. sadisplay::
    :module: briefy.leica.models.customer
    :alt: Customer data model
    :render: plantuml


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


Job Locations
+++++++++++++

Inheritance diagram for the Job location class:

.. inheritance-diagram:: briefy.leica.models.job_location.JobLocation


Database diagram for the JobLocation data model:

.. sadisplay::
    :module: briefy.leica.models.job_location
    :alt: Job locations data model
    :render: plantuml


id (uuid)
    Unique identifier using function :func:`uuid.uuid4`.

    From :class:`briefy.common.db.mixins.identifiable.GUID`.

job_id (uuid)
    Foreign key to :class:`briefy.leica.models.job.Job`.

coordinates (geometry:point)
    Map point defined as sub type of :class:`geoalchemy2.Geometry`
    in :class:`briefy.common.db.types.geo.POINT`.

    Class attribute: _coordinates
    Property: coordinates
    From :class:`briefy.common.db.mixins.address.Address`.

state_history (json)
    History of workflow transitions one instance had.

    Class attribute: _state_history
    Property: state_history
    From :class:`briefy.common.db.mixins.workflow.Workflow`.

country (string)
    Two letter country code managed by type :class:`sqlalchemy_utils.CountryType`.

    From :class:`briefy.common.db.mixins.address.Address`.

created_at (datetime)
    Date time (UTC) of the object creation.

    From :class:`briefy.common.db.mixins.timestamp.Timestamp`.

info (json)
    Raw data (json) of the location information returned by google maps API.

    From :class:`briefy.common.db.mixins.address.Address`.

locality (string)
    Name of the locality (city or similar).

    From :class:`briefy.common.db.mixins.address.Address`.

state (string)
    Current workflow state of the instance.

    From :class:`briefy.common.db.mixins.workflow.Workflow`.

timezone (string)
    Timezone information of the location managed by type :class:`sqlalchemy_utils.TimezoneType`.

    From :class:`briefy.common.db.mixins.address.Address`.

updated_at (datetime)
    Date time (UTC) of the last change.

    From :class:`briefy.common.db.mixins.timestamp.Timestamp`.

job (relation)
    Reference to the Job instance related to the JobLocation.

Job
+++

Inheritance diagram for the Job class:

.. inheritance-diagram:: briefy.leica.models.job.Job


Database diagram for the Job data model:

.. sadisplay::
    :module: briefy.leica.models.job
    :alt: Job data model
    :render: plantuml


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

Project
+++++++

Inheritance diagram for the Project class:

.. inheritance-diagram:: briefy.leica.models.project.Project


Database diagram for the Project data model:

.. sadisplay::
    :module: briefy.leica.models.project
    :alt: Project data model
    :render: plantuml


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


ER diagram
++++++++++

Complete database models ER diagram.


.. sadisplay::
    :module: briefy.leica.models
    :link:
    :alt: Briefy Leica database models diagram.
    :render: plantuml