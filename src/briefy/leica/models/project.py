
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
from zope.interface import Interface

import sqlalchemy as sa
import sqlalchemy_utils as sautils



class IProject(Interface):
    """Marker interface for Job"""


class Project(Mixin, Base):
    implements(IProject)
    version = None
    url = ''
    comments = ''

    _workflow = ProjectWorkflow
    __tablename__ = "project"
    __session__ = Session
