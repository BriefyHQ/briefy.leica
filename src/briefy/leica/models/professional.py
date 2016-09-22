"""Briefy Leica Professional model."""
from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins import BaseMetadata
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows
from zope.interface import Interface
from zope.interface import implementer

import colander
import sqlalchemy as sa


class IProfessional(Interface):
    """Marker interface for a Professional"""


@implementer(IProfessional)
class Professional(BaseMetadata, Mixin, Base):
    """Professional model."""

    version = None

    __tablename__ = "professionals"
    __session__ = Session
    _workflow = workflows.ProfessionalWorkflow

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', '_slug']}

    jobs = sa.orm.relationship('Job', back_populates='professional')
    external_id = sa.Column(sa.String,
                            nullable=True,
                            info={'colanderalchemy': {
                                'title': 'External ID',
                                'missing': colander.drop}}
                            )

    def __repr__(self):
        return '<Professional-proxy \'{0}\'>'.format(self.display_name)
