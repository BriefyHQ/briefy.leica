from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins import Address as AddressMixin
from briefy.common.db.mixins.optin import OptIn
from .workflows.utils import with_workflow
from briefy.leica.db import Base
from briefy.leica.db import Session
from sqlalchemy import orm
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState
from briefy.common.workflow import WorkflowTransition
from enum import Enum
from zope.interface import implementer
from zope.interface import Interface

from .types import CategoryChoices
from .types import SchedulingIssuesChoices
from .types import ClientJobStatusChoices
from .types import JobContinentChoices


import sqlalchemy as sa
import sqlalchemy_utils as sautils



class JobWorkflow(BriefyWorkflow):
    """Workflow for an Asset."""

    # Optional name for this workflow
    entity = 'job'
    initial_state = 'created'

    # States
    created = WorkflowState('created', title='Created', description='Asset created')
    aproved = WorkflowState('photoset_is_ok', title='Photoset is ok', description='Photos aproved for delivery')

class IJob(Interface):
    """Marker interface for Job"""


class JobLocation(Mixin, AddressMixin, Base):
    version = None
    url = ''
    comments = ''

    _workflow = JobWorkflow
    __tablename__ = "job_location"
    __session__ = Session


@implementer(IJob)
class Job(Mixin, Base):
    version = None
    url = ''
    comments = ''

    _workflow = JobWorkflow
    __tablename__ = "job"
    __session__ = Session

    # Fields to update on workflow changes:
    # approval_status = sa.Column(sa.String(), nullable=True) # multiple_choice
    # assigned = sa.Column(sa.String(), nullable=True) # boolean
    # assignment_date = sa.Column(sa.String(), nullable=True) # date_time
    # input_date = sa.Column(sa.String(), nullable=True) # date_time
    # input_person = sa.Column(sa.String(), nullable=True) # connection
    # input_source = sa.Column(sa.String(), nullable=True) # multiple_choice
    # internal_comments = sa.Column(sa.String(), nullable=True) # paragraph_text
    # job_id = sa.Column(sa.String(), nullable=True) # extr=external_reference
    # job_name = sa.Column(sa.String(), nullable=True) # short_text
    # last_approval_date = sa.Column(sa.String(), nullable=True) # date_time
    # submission_date = sa.Column(sa.String(), nullable=True) # date_time
    # update_completed = sa.Column(sa.String(), nullable=True) # boolean

    external_reference = sa.Column(sa.String())
    title = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    internal_job_id = sa.Column(sa.String(), nullable=True)

    availability_1 = sa.Column(sa.DateTime(), nullable=True)
    availability_2 = sa.Column(sa.DateTime(), nullable=True)

    category = sa.Column(sautils.ChoiceType(CategoryChoices, impl=sa.String()), nullable=True)

    client_delivery_link = sa.Column(sa.String(), nullable=True) # link
    client_feedback = sa.Column(sa.String(), nullable=True) # paragraph_text
    client_job_status = sa.Column(sautils.ChoiceType(
        ClientJobStatusChoices, impl=sa.String()),
        nullable=True)
    client_specific_requirement = sa.Column(sa.String(), nullable=True) # paragraph_text
    # Not an SQLAlchemy foreign key, because company is actually in an external service
    company_id = sa.Column(sautils.UUIDType, nullable=True) # connection

    contact_person_id = sa.Column(sautils.UUIDType, nullable=True) # connection

    currency_payout = sa.Column(sa.String(), nullable=True) # multiple_choice

    finance_manager = sa.Column(sautils.UUIDType, nullable=True)

    finance_manager_to_payout = sa.Column(sautils.UUIDType, nullable=True)

    invoice_date = sa.Column(sa.DateTime(), nullable=True) # date_time

    # job_continent = sa.Column(sautils.ChoiceType(JobContinentChoices, impl=sa.String()), nullable=True)

    job_location_id = sa.Column(sa.ForeignKey('job_location.id'), nullable=True)
    job_location = sa.orm.relationship('JobLocation')

    payout_date = sa.Column(sa.DateTime(), nullable=True)
    photo_submission_link = sa.Column(sa.String(), nullable=True) # link

    photographer_payout = sa.Column(sa.String(), nullable=True) # number

    photographers_comment = sa.Column(sa.String(), nullable=True) # paragraph_text


    project_id = sa.Column(sa.ForeignKey('project.id'), nullable=False)
    project = sa.orm.relationship('Project')

    project_manager_comment = sa.Column(sa.String(), nullable=True)
    qa_manager = sa.Column(sautils.UUIDType, nullable=True)
    quality_assurance_feedback = sa.Column(sa.String(), nullable=True)

    responsible_photographer = sa.Column(sautils.UUIDType, nullable=True)

    scheduled_shoot_date_time = sa.Column(sa.DateTime(), nullable=True) # date_time

    scheduling_issues = sa.Column(sautils.ChoiceType(
        SchedulingIssuesChoices, impl=sa.String()),
        nullable=True
    )

    scouting_manager = sa.Column(sautils.UUIDType, nullable=True)

    set_price = sa.Column(sa.String(), nullable=True) # number
    signed_releases_contract = sa.Column(sautils.UUIDType, nullable=True) # file

    travel_expenses = sa.Column(sa.String(), nullable=True) # number

    assets = sa.orm.relationship('Asset', back_populates='job', secondary='job_assets')



job_assets = sa.Table(
    'job_assets', Base.metadata,
     sa.Column(
         'job_uid', sautils.UUIDType,
          sa.ForeignKey('job.id')
     ),
     sa.Column(
         'asset_uid', sautils.UUIDType,
          sa.ForeignKey('asset.id')
     )
)



