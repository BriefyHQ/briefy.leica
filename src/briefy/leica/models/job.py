"""Briefy Leica Job model."""
from briefy.common.db.mixins import Mixin
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows
from sqlalchemy import orm
from zope.interface import implementer
from zope.interface import Interface

from .types import CategoryChoices
from .types import SchedulingIssuesChoices
from .types import ClientJobStatusChoices

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class IJob(Interface):
    """Marker interface for Job"""


@implementer(IJob)
class Job(Mixin, Base):
    """Job model."""
    version = None
    url = ''

    _workflow = workflows.JobWorkflow
    __tablename__ = "jobs"
    __session__ = Session

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', 'project',
                                               'comments', 'internal_comments']}

    # Fields to update on workflow changes:
    # approval_status = sa.Column(sa.String(), nullable=True) # multiple_choice
    # assigned = sa.Column(sa.String(), nullable=True) # boolean
    # assignment_date = sa.Column(sa.String(), nullable=True) # date_time
    # input_date = sa.Column(sa.String(), nullable=True) # date_time
    # input_person = sa.Column(sa.String(), nullable=True) # connection
    # input_source = sa.Column(sa.String(), nullable=True) # multiple_choice
    # internal_comments = sa.Column(sa.String(), nullable=True) # paragraph_text
    # last_approval_date = sa.Column(sa.String(), nullable=True) # date_time
    # submission_date = sa.Column(sa.String(), nullable=True) # date_time
    # update_completed = sa.Column(sa.String(), nullable=True) # boolean
    # job_continent = sa.Column(sautils.ChoiceType(JobContinentChoices,
    #                           impl=sa.String), nullable=True)

    title = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, default='')
    internal_job_id = sa.Column(sa.String, nullable=False)
    customer_job_id = sa.Column(sa.String, default='')
    availability_1 = sa.Column(sa.DateTime,
                               default=None,
                               info={'colanderalchemy': {
                                   'title': 'Availability date 1',
                                   'missing': None,
                                   'typ': colander.DateTime}}
                               )
    availability_2 = sa.Column(sa.DateTime,
                               default=None,
                               info={'colanderalchemy': {
                                   'title': 'Availability date 2',
                                   'missing': None,
                                   'typ': colander.DateTime}}
                               )
    category = sa.Column(sautils.ChoiceType(CategoryChoices, impl=sa.String()),
                         default='undefined',
                         nullable=True)
    client_delivery_link = sa.Column(sautils.URLType, nullable=True)
    client_feedback = sa.Column(sa.Text, default='')
    client_job_status = sa.Column(sautils.ChoiceType(ClientJobStatusChoices, impl=sa.String()),
                                  default='undefined',
                                  nullable=True)
    client_specific_requirement = sa.Column(sa.Text, default='')

    company_id = sa.Column(sautils.UUIDType,
                           nullable=True,
                           info={'colanderalchemy': {
                               'title': 'Company ID',
                               'validator': colander.uuid,
                               'missing': None,
                               'typ': colander.String}}
                           )

    contact_person_id = sa.Column(sautils.UUIDType,
                                  nullable=True,
                                  info={'colanderalchemy': {
                                      'title': 'Contact ID',
                                      'validator': colander.uuid,
                                      'missing': None,
                                      'typ': colander.String}}
                                  )

    currency_payout = sa.Column(sautils.CurrencyType, default='EUR')
    finance_manager = sa.Column(sautils.UUIDType,
                                nullable=True,
                                info={'colanderalchemy': {
                                    'title': 'Finance Manager ID',
                                    'validator': colander.uuid,
                                    'missing': None,
                                    'typ': colander.String}}
                                )

    finance_manager_to_payout = sa.Column(sautils.UUIDType,
                                          nullable=True,
                                          info={'colanderalchemy': {
                                              'title': 'Finance Manager Payout ID',
                                              'validator': colander.uuid,
                                              'missing': None,
                                              'typ': colander.String}}
                                          )

    invoice_date = sa.Column(sa.DateTime,
                             default=None,
                             info={'colanderalchemy': {
                                 'title': 'Invoice Date',
                                 'missing': None,
                                 'typ': colander.DateTime}}
                             )
    job_locations = sa.orm.relationship('JobLocation')
    payout_date = sa.Column(sa.DateTime,
                            default=None,
                            info={'colanderalchemy': {
                                'title': 'Payout date',
                                'missing': None,
                                'typ': colander.DateTime}}
                            )
    photo_submission_link = sa.Column(sautils.URLType, nullable=True)
    photographer_payout = sa.Column(sa.Integer,
                                    nullable=True,
                                    info={'colanderalchemy': {
                                        'title': 'Price',
                                        'missing': None,
                                        'typ': colander.Integer}}
                                    )
    photographers_comment = sa.Column(sa.Text, default='')

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
    project_manager_comment = sa.Column(sa.Text, default='')
    qa_manager = sa.Column(sautils.UUIDType,
                           nullable=True,
                           info={'colanderalchemy': {
                               'title': 'QA Manager ID',
                               'validator': colander.uuid,
                               'missing': None,
                               'typ': colander.String}}
                           )
    quality_assurance_feedback = sa.Column(sa.Text, default='')
    responsible_photographer = sa.Column(sautils.UUIDType,
                                         nullable=True,
                                         info={'colanderalchemy': {
                                             'title': 'Professional ID',
                                             'validator': colander.uuid,
                                             'missing': None,
                                             'typ': colander.String}}
                                         )
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
    scouting_manager = sa.Column(sautils.UUIDType,
                                 nullable=True,
                                 info={'colanderalchemy': {
                                     'title': 'Scouting Manager ID',
                                     'validator': colander.uuid,
                                     'missing': None,
                                     'typ': colander.String}}
                                 )
    price = sa.Column(sa.Integer,
                      nullable=True,
                      info={'colanderalchemy': {
                          'title': 'Price',
                          'missing': None,
                          'typ': colander.Integer}}
                      )
    signed_releases_contract = sa.Column(sautils.UUIDType,
                                         nullable=True,
                                         info={'colanderalchemy': {
                                             'title': 'Contract ID',
                                             'validator': colander.uuid,
                                             'missing': None,
                                             'typ': colander.String}}
                                         )
    travel_expenses = sa.Column(sa.Integer,
                                nullable=True,
                                info={'colanderalchemy': {
                                    'title': 'Price',
                                    'missing': None,
                                    'typ': colander.Integer}}
                                )
    assets = sa.orm.relationship('Asset', back_populates='job')
    comments = sa.orm.relationship('Comment',
                                   foreign_keys='Comment.entity_id',
                                   primaryjoin='Comment.entity_id == Job.id')
    internal_comments = sa.orm.relationship('InternalComment',
                                            foreign_keys='InternalComment.entity_id',
                                            primaryjoin='InternalComment.entity_id == Job.id')
