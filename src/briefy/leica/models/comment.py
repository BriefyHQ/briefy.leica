"""Briefy Leica Comment model."""
from briefy.common.db.mixins import Mixin
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows
from zope.interface import implementer
from zope.interface import Interface

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class IComment(Interface):
    """Marker interface for a Comment"""


@implementer(IComment)
class Comment(Mixin, Base):

    __tablename__ = 'comments'
    __session__ = Session
    _workflow = workflows.CommentWorkflow

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', 'entity_type', 'type']}

    type = sa.Column(sa.String(50))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'comment'
    }

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


class InternalComment(Comment):

    __mapper_args__ = {
        'polymorphic_identity': 'internal_comment'
    }
