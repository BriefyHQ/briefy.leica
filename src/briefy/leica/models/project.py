
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
from zope.interface import implementer

import sqlalchemy as sa
import sqlalchemy_utils as sautils


class ProjectWorkflow(BriefyWorkflow):
    pass

class IProject(Interface):
    """Marker interface for Job"""

@implementer(IProject)
class Project(Mixin, Base):
    version = None
    url = ''
    comments = ''

    _workflow = ProjectWorkflow
    __tablename__ = "project"
    __session__ = Session
