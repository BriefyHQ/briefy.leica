Asset
-----

Inheritance
+++++++++++

Inheritance diagram for the Asset class:

.. inheritance-diagram:: briefy.leica.models.asset.Asset


Attributes
++++++++++

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


State Machine
+++++++++++++

.. uml::

    @startuml

    title Asset Workflow

    state created: Inserted on the Database
    state validation: Under machine\nvalidation
    state edit: Professional needs to\nwork on the Asset
    state deleted: Professional deletes\nan Asset
    state pending: Under QA evaluation
    state discarded: Not going\nto be used
    state post_processing: Internal\npost processing
    state approved: Approved by QA
    state reserved: Will not be delivered\nbut is available for Briefy.
    state refused: Customer refused\nthe Asset.

    [*] --> created
    created --> validation : submit\n(Professional)
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


Database model
++++++++++++++

Database diagram for the Asset data model:


.. sadisplay::
    :module: briefy.leica.models.asset
    :alt: Asset data model
    :render: graphviz
