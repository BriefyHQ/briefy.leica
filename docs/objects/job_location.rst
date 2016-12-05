Job Location
------------

Inheritance
+++++++++++

Inheritance diagram for the Job location class:

.. inheritance-diagram:: briefy.leica.models.job.location.JobLocation



Attributes
++++++++++

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


State Machine
+++++++++++++

.. uml::

    @startuml

    title Job Location Workflow

    state created: Inserted on the Database

    [*] --> created

    @enduml


Database model
++++++++++++++

Database diagram for the JobLocation data model:

.. sadisplay::
    :module: briefy.leica.models.job.location
    :alt: Job locations data model
    :render: graphviz
