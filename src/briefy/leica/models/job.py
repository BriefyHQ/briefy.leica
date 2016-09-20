"""Briefy Leica Job model."""
from .types import CategoryChoices
from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins import BriefyRoles
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows

from zope.interface import implementer
from zope.interface import Interface

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class IJob(Interface):
    """Marker interface for Job"""


@implementer(IJob)
class Job(BriefyRoles, Mixin, Base):
    """A Job within a project."""

    version = None

    _workflow = workflows.JobWorkflow
    __tablename__ = 'jobs'
    __session__ = Session

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', 'project',
                                               'comments', 'internal_comments']}

    project_id = sa.Column(sautils.UUIDType,
                           sa.ForeignKey('projects.id'),
                           nullable=False,
                           info={'colanderalchemy': {
                               'title': 'Project ID',
                               'validator': colander.uuid,
                               'missing': None,
                               'typ': colander.String}}
                           )

    project = sa.orm.relationship('Project', uselist=False, back_populates='jobs')

    # Professional
    professional = sa.Column(sautils.UUIDType,
                             nullable=True,
                             info={'colanderalchemy': {
                                   'title': 'Professional',
                                   'validator': colander.uuid,
                                   'missing': None,
                                   'typ': colander.String}}
                             )
    # Job details
    title = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, default='')
    job_requirements = sa.Column(sa.Text, default='')
    job_locations = sa.orm.relationship('JobLocation')

    # Category of the job # TODO: need to come from briefy.common
    category = sa.Column(sautils.ChoiceType(CategoryChoices, impl=sa.String()),
                         default='undefined',
                         nullable=True)

    # Job Identifiers
    job_id = sa.Column(sa.String, nullable=False)  # Was internal_job_id
    customer_job_id = sa.Column(sa.String, default='')  # Id on the customer database

    assets = sa.orm.relationship('Asset', back_populates='job')
    comments = sa.orm.relationship('Comment',
                                   foreign_keys='Comment.entity_id',
                                   primaryjoin='Comment.entity_id == Job.id')
    internal_comments = sa.orm.relationship('InternalComment',
                                            foreign_keys='InternalComment.entity_id',
                                            primaryjoin='InternalComment.entity_id == Job.id')

    @property
    def customer(self):
        """Customer hiring this job."""
        return self.project.customer

    @property
    def project_manager(self):
        """Return the project manager responsible for this job."""
        return self.project.project_manager

    @property
    def price(self) -> int:
        """Price of this job.

        :return: Return the price, in cents, of this job.
        """
        price = self._price
        if not price:
            price = self.project.price
        return price

    @property
    def external_status(self) -> str:
        """Status of this job to be displayed to the customer.

        :return: A friendly name for the workflow state.
        """
        # TODO: Use a mapping
        status = self.workflow.state.name
        return status

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['comments'] = self.comments
        return data
