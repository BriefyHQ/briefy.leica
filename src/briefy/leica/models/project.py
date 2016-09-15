"""Briefy Leica Project model."""
from briefy.common.db.mixins import Mixin
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows
from sqlalchemy import orm
from zope.interface import Interface
from zope.interface import implementer

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class IProject(Interface):
    """Marker interface for Job"""


@implementer(IProject)
class Project(Mixin, Base):
    """Project model."""
    version = None
    url = ''
    comments = ''

    __tablename__ = "projects"
    __session__ = Session
    _workflow = workflows.ProjectWorkflow

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state']}

    briefing = sa.Column(sa.Text, default='')  # file
    company_id = sa.Column(sautils.UUIDType,
                           nullable=False,
                           info={'colanderalchemy': {
                               'title': 'ID',
                               'validator': colander.uuid,
                               'typ': colander.String}}
                           )
    currency_set_price = sa.Column(sautils.CurrencyType, default='EUR')

    abstract = sa.Column(sa.Text, default='')  # paragraph_text
    manager = sa.Column(sa.String, default='')  # connection
    name = sa.Column(sa.String, nullable=False)  # short_text
    set_price = sa.Column(sa.Integer, nullable=False)  # number
    release_template = sa.Column(sautils.URLType, nullable=True)  # link to knack for now

    # property
    # total_sum_of_jobs_in_project = sa.Column(sa.String(), nullable=True)  # su

    req_iso = sa.Column(sa.String, default='')
    req_aperture = sa.Column(sa.String, default='')
    req_aspect_ratio = sa.Column(sa.String, default='')
    req_resolution = sa.Column(sa.Integer,
                               info={'colanderalchemy': {
                                   'title': 'Required Resolution',
                                   'missing': None,
                                   'typ': colander.Integer}}
                               )
    req_size = sa.Column(sa.String, default='1600x1200')

    jobs = sa.orm.relationship('Job', back_populates='project')
