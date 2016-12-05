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
    """Marker interface for a Comment"""


@implementer(IComment)
class Comment(mixins.LeicaMixin, Base):

    _workflow = workflows.CommentWorkflow

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', 'entity_type', 'type']}

    content = sa.Column(sa.Text, nullable=False)
    comment_order = sa.Column(sa.Integer, default=0)
    author_id = sa.Column(sautils.UUIDType,
                          nullable=False,
                          info={'colanderalchemy': {
                              'title': 'ID',
                              'validator': colander.uuid,
                              'typ': colander.String}}
                          )

    in_reply_to = sa.Column(sautils.UUIDType,
                            sa.ForeignKey('comments.id'),
                            nullable=True,
                            info={'colanderalchemy': {
                                'title': 'Parent comment',
                                'validator': colander.uuid,
                                'missing': None,
                                'typ': colander.String}}
                            )

    entity_type = sa.Column(sa.String(255))
    entity_id = sa.Column(sautils.UUIDType,
                          info={'colanderalchemy': {
                              'title': 'ID',
                              'validator': colander.uuid,
                              'typ': colander.String}}
                          )

    entity = sautils.generic_relationship(entity_type, entity_id)

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        add_user_info_to_state_history(self.state_history)
        return data
