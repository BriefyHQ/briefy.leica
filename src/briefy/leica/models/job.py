from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins.optin import OptIn
from .workflows.utils import with_workflow
from briefy.leica.db import Base
from briefy.leica.db import Session
from sqlalchemy import orm
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState
from briefy.common.workflow import WorkflowTransition

import sqlalchemy as sa
import sqlalchemy_utils as sautils




class JobWorkflow(BriefyWorkflow):
    """Workflow for an Asset."""

    # Optional name for this workflow
    entity = 'job'
    initial_state = 'created'

    # States
    created = WorkflowState('created', title='Created', description='Asset created')
    aproved = WorkflowState('photoset_is_ok', title='Photset is ok', description='Photos aproved for delivery')



class Job(Mixin, Base):
    version = None
    url = ''
    comments = ''

    _workflow = JobWorkflow
    __tablename__ = "jobs"


    id = sa.Column(sautils.UUIDType, nullable=False)
    external_reference = sa.Column(sautils.String())
    title = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)



