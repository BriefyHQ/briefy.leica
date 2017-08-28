"""Custom briefy.leica events for model Comment and InternalComment."""
from briefy.common.db.models import Item
from briefy.leica import logger
from briefy.ws.resources import events

import typing as t


Attributes = t.Optional[t.List[str]]


def to_dict_with_entity_lr(comment: Item, excludes: Attributes=None, includes: Attributes=None):
    """Create the comment serializable data appending local roles from the commented entity.

    :param comment: Comment instance.
    :param excludes: attributes to exclude from obj representation.
    :param includes: attributes to include from obj representation.
    :returns: Dictionary with fields and values of the comment instance plus entity lr.
    """
    data = comment.to_dict(excludes=excludes, includes=includes)
    entity = comment.entity
    entity_data = comment.entity.to_dict()
    if isinstance(entity, Item):
        data['_roles'] = entity_data.get('_roles')
        data['_actors'] = entity_data.get('_actors')
    return data


class CommentCreatedEvent(events.ObjectCreatedEvent):
    """Event to notify comment creation."""

    event_name = 'comment.created'
    logger = logger

    def to_dict(self, excludes: Attributes=None, includes: Attributes=None) -> dict:
        """Return a serializable dictionary from the object that generated this event.

        :param excludes: attributes to exclude from dict representation.
        :param includes: attributes to include from dict representation.
        :returns: Dictionary with fields and values of comment instance plus entity lr.
        """
        return to_dict_with_entity_lr(self.obj, excludes=excludes, includes=includes)


class CommentUpdatedEvent(events.ObjectUpdatedEvent):
    """Event to notify comment update."""

    event_name = 'comment.updated'
    logger = logger

    def to_dict(self, excludes: Attributes=None, includes: Attributes=None) -> dict:
        """Return a serializable dictionary from the object that generated this event.

        :param excludes: attributes to exclude from dict representation.
        :param includes: attributes to include from dict representation.
        :returns: Dictionary with fields and values of comment instance plus entity lr.
        """
        return to_dict_with_entity_lr(self.obj, excludes=excludes, includes=includes)


class CommentDeletedEvent(events.ObjectDeletedEvent):
    """Event to notify comment delete."""


class CommentLoadedEvent(events.ObjectLoadedEvent):
    """Event to notify comment load."""
