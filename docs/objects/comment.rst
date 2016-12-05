Comment
-------

Inheritance
+++++++++++

Inheritance diagram for the Comment class:

.. inheritance-diagram:: briefy.leica.models.comment.Comment


Attributes
++++++++++

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

State Machine
+++++++++++++

.. uml::

    @startuml

    title Comment Workflow

    state created: Inserted on the Database

    [*] --> created


    @enduml


Database model
++++++++++++++

Database diagram for the Comment data model:

.. sadisplay::
    :module: briefy.leica.models.comment
    :alt: Comment data model
    :render: graphviz