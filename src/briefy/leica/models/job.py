"""Briefy Leica Job model."""
from .types import CategoryChoices
from .types import ClientJobStatusChoices
from .types import SchedulingIssuesChoices
from briefy.common.db.mixins import Mixin
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows
from sqlalchemy.ext.hybrid import hybrid_property
from zope.interface import implementer
from zope.interface import Interface

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class FinancialInfo:
    """Mixin containing financial information."""

    payout_currency = sa.Column(sautils.CurrencyType, default='EUR')
    payout_value = sa.Column(sa.Integer,
                             nullable=True,
                             info={'colanderalchemy': {
                                   'title': 'Price',
                                   'missing': None,
                                   'typ': colander.Integer}}
                            )

    _price = sa.Column(
        'price',
        sa.Integer,
        nullable=True,
        info={'colanderalchemy': {
            'title': 'Set Price',
            'missing': None,
            'typ': colander.Integer}}
        )

    travel_expenses = sa.Column(sa.Integer,
                                nullable=True,
                                info={'colanderalchemy': {
                                    'title': 'Travel Expenses',
                                    'missing': None,
                                    'typ': colander.Integer}}
                                )

    @property
    def price(self) -> int:
        """Price of this job.

        :return: Return the price, in cents, of this job.
        """
        return self._price


class InternalRoles:
    """Internal roles for this job."""

    finance_manager = sa.Column(sautils.UUIDType,
                                nullable=True,
                                info={'colanderalchemy': {
                                    'title': 'Finance Manager ID',
                                    'validator': colander.uuid,
                                    'missing': None,
                                    'typ': colander.String}}
                                )


    qa_manager = sa.Column(sautils.UUIDType,
                           nullable=True,
                           info={'colanderalchemy': {
                               'title': 'QA Manager ID',
                               'validator': colander.uuid,
                               'missing': None,
                               'typ': colander.String}}
                           )

    scouting_manager = sa.Column(sautils.UUIDType,
                                 nullable=True,
                                 info={'colanderalchemy': {
                                     'title': 'Scouting Manager ID',
                                     'validator': colander.uuid,
                                     'missing': None,
                                     'typ': colander.String}}
                                 )


class IJob(Interface):
    """Marker interface for Job"""


@implementer(IJob)
class Job(InternalRoles, FinancialInfo, Mixin, Base):
    """A Job within a project."""

    version = None

    _workflow = workflows.JobWorkflow
    __tablename__ = 'jobs'
    __session__ = Session

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', 'project',
                                               'comments', 'internal_comments']}

    # Project
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
    requirements = sa.Column('requirements', sautils.JSONType)  # Structured job requirements
    job_locations = sa.orm.relationship('JobLocation')
    # Category of the job # TODO: need to come from briefy.common
    category = sa.Column(sautils.ChoiceType(CategoryChoices, impl=sa.String()),
                         default='undefined',
                         nullable=True)

    # Job Identifiers
    job_id = sa.Column(sa.String, nullable=False)  # Was internal_job_id
    customer_job_id = sa.Column(sa.String, default='')  # Id on the customer database

    # Availability
    # TODO: Add colanderalchemy validation of a list of dates
    availability = sa.Column(sautils.JSONType,
                             default=None,
                             info={'colanderalchemy': {
                                   'title': 'Availability',
                                   'missing': None,
                                   'typ': colander.List}
                             })

    scheduled_shoot_date_time = sa.Column(sa.DateTime,
                                          default=None,
                                          info={'colanderalchemy': {
                                              'title': 'Scheduled shoot date',
                                              'missing': None,
                                              'typ': colander.DateTime}}
                                          )
    scheduling_issues = sa.Column(sautils.ChoiceType(SchedulingIssuesChoices,
                                                     impl=sa.String()),
                                  default='undefined',
                                  nullable=True)



    signed_releases_contract = sa.Column(sautils.UUIDType,
                                         nullable=True,
                                         info={'colanderalchemy': {
                                             'title': 'Contract ID',
                                             'validator': colander.uuid,
                                             'missing': None,
                                             'typ': colander.String}}
                                         )

    assets = sa.orm.relationship('Asset', back_populates='job')

    comments = sa.orm.relationship('Comment',
                                   foreign_keys='Comment.entity_id',
                                   primaryjoin='Comment.entity_id == Job.id')

    internal_comments = sa.orm.relationship('InternalComment',
                                            foreign_keys='InternalComment.entity_id',
                                            primaryjoin='InternalComment.entity_id == Job.id')


    @hybrid_property
    def customer(self):
        """Customer hiring this job."""
        return self.project.customer

    @property
    def project_manager(self):
        """Return the project manager responsible for this job."""
        return self.project.manager

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