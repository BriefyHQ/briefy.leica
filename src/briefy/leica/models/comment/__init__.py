"""Briefy Leica Comment model."""
from briefy.leica.cache import cache_manager
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.comment import workflows
from sqlalchemy import event
from zope.interface import implementer
from zope.interface import Interface

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class IComment(Interface):
    """Marker interface for a Comment."""


@implementer(IComment)
class Comment(mixins.LeicaMixin, Base):
    """A comment to an object."""

    _workflow = workflows.CommentWorkflow

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', 'type']}

    __summary_attributes__ = [
        'id', 'content', 'internal', 'created_at', 'updated_at', 'author', 'author_role', 'to_role'
    ]

    __exclude_attributes__ = ['entity']

    __to_dict_additional_attributes__ = ['author']

    __listing_attributes__ = __summary_attributes__

    __raw_acl__ = (
        ('list', ('g:briefy', 'g:system')),
        ('create', ('g:briefy', 'g:professionals', 'g:customers', 'g:system')),
        ('view', ('g:briefy', 'g:professionals', 'g:customers', 'g:system')),
        ('edit', ('g:briefy', 'g:system',)),
        ('delete', ('g:system',)),
    )

    content = sa.Column(sa.Text, nullable=False)
    """Content.

    Main body of a comment
    """

    comment_order = sa.Column(sa.Integer, default=0)
    """Comment order.

    The cronolgical order in which this comment was added
    to its target subject
    """
    author_id = sa.Column(sautils.UUIDType,
                          nullable=False,
                          info={'colanderalchemy': {
                              'title': 'ID',
                              'validator': colander.uuid,
                              'typ': colander.String}}
                          )
    """Author ID."""

    author_role = sa.Column(sa.String,
                            nullable=False,
                            info={'colanderalchemy': {
                                  'title': 'Author Role',
                                  'typ': colander.String}}
                            )
    """Primary role of the author."""

    to_role = sa.Column(sa.String,
                        nullable=False,
                        info={'colanderalchemy': {
                              'title': 'Destination Role',
                              'typ': colander.String}}
                        )
    """Destination role that should see the comment."""

    in_reply_to = sa.Column(sautils.UUIDType,
                            sa.ForeignKey('comments.id'),
                            index=True,
                            nullable=True,
                            info={'colanderalchemy': {
                                'title': 'Parent comment',
                                'validator': colander.uuid,
                                'missing': None,
                                'typ': colander.String}}
                            )
    """In Reply To.

    Comment which this one replies. Used for establishing comment threads.
    """

    internal = sa.Column(sa.Boolean, default=True)
    """Internal comment flag.

    Mark if the comment should only be visible internal.

    """

    entity_type = sa.Column(
        sa.String(255),
        nullable=False,
        info={'colanderalchemy': {
            'title': 'entity',
            'typ': colander.String}
        }
    )
    """Entity Type.

    To which object type (model) this comment is attached to.

    """
    entity_id = sa.Column(sautils.UUIDType,
                          info={'colanderalchemy': {
                              'title': 'ID',
                              'validator': colander.uuid,
                              'typ': colander.String}}
                          )
    """Entity ID.

    Entity this comment is attached to.
    """

    @property
    def author(self):
        """Author information."""
        return mixins.get_public_user_info(str(self.author_id))

    entity = sautils.generic_relationship(entity_type, entity_id)


@event.listens_for(Comment, 'after_update')
def assignment_after_update(mapper, connection, target):
    """Invalidate Comment (and related entity) cache after instance update."""
    cache_manager.refresh(target)
    if target.entity:
        cache_manager.refresh(target.entity)
