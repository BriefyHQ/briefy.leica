"""Briefy Leica Job location model."""
from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins import Address as AddressMixin
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class JobLocation(Mixin, AddressMixin, Base):
    """Job location model."""
    version = None
    url = ''
    comments = ''

    _workflow = workflows.JobWorkflow
    __tablename__ = 'job_locations'
    __session__ = Session

    job_id = sa.Column(sautils.UUIDType,
                       sa.ForeignKey('jobs.id'),
                       nullable=False,
                       info={'colanderalchemy': {
                           'title': 'ID',
                           'validator': colander.uuid,
                           'typ': colander.String}}
                       )
    job = sa.orm.relationship('Job', uselist=False)
