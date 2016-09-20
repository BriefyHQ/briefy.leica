"""Briefy Leica Project model."""
from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import BriefyRoles
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows
from zope.interface import Interface
from zope.interface import implementer

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class IProject(Interface):
    """Marker interface for Job"""


@implementer(IProject)
class Project(BriefyRoles, BaseMetadata, Mixin, Base):
    """Project model."""
    version = None

    __tablename__ = "projects"
    __session__ = Session
    _workflow = workflows.ProjectWorkflow

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', 'customer']}
    customer_id = sa.Column(sautils.UUIDType,
                            sa.ForeignKey('customers.id'),
                            nullable=False,
                            info={'colanderalchemy': {
                               'title': 'Customer',
                               'validator': colander.uuid,
                               'typ': colander.String}}
                            )
    customer = sa.orm.relationship('Customer', back_populates='projects')

    external_id = sa.Column(sa.String)

    """
    {
    "dimensions": "3000x2000",
    #TODO: formalize these

    }

    """
    tech_requirements = sa.Column(sautils.JSONType,
                                  info={'colanderalchemy': {
                                       'title': 'Required Resolution',
                                       'missing': colander.drop,
                                       'typ': colander.String}}
                                  )

    jobs = sa.orm.relationship('Job', back_populates='project')
