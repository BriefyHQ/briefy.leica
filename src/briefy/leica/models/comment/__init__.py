"""Briefy Leica Comment model."""
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.comment import workflows
from briefy.ws.utils.user import add_user_info_to_state_history
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

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', 'entity_type', 'type']}

    __raw_acl__ = (
        ('list', ('g:briefy', 'g:system')),
        ('create', ('g:briefy', 'g:system')),
        ('view', ('g:briefy', 'g:system')),
        ('edit', ('g:system',)),
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

    in_reply_to = sa.Column(sautils.UUIDType,
                            sa.ForeignKey('comments.id'),
                            nullable=True,
                            info={'colanderalchemy': {
                                'title': 'Parent comment',
                                'validator': colander.uuid,
                                'missing': None,
                                'typ': colander.String}}
                            )
    """In Reply To.

    Comment which this one replies. Used for stablishing comment threads.
    """

    entity_type = sa.Column(sa.String(255))
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

    entity = sautils.generic_relationship(entity_type, entity_id)

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        add_user_info_to_state_history(self.state_history)
        return data
