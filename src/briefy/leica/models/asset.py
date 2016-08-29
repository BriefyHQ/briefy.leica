from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins.optin import OptIn
from briefy.leica.db import Base
from briefy.leica.db import Session
from sqlalchemy import orm

import sqlalchemy as sa
import sqlalchemy_utils as sautils



from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState
from briefy.common.workflow import WorkflowTransition


class AssetWorkflow(BriefyWorkflow):
    """Workflow for a Lead."""

    # Optional name for this workflow
    entity = 'lead'
    initial_state = 'created'

    # States
    created = WorkflowState('created', title='Created', description='Asset created')
    staff_action = WorkflowState('staff_action', title='staff_action_required', description='Staff Action Required')
    author_action = WorkflowState('author_action', title='author_action_required', description='Author Action Required')
    aproved = WorkflowState('aproved', title='aproved', description='Asset Aproved')
    rejected = WorkflowState('rejected', title='Rejected', description='Asset Rejected')
    delivered = WorkflowState('delivered', title='delivered', description='Asset Delivered')

    # Transitions
    request_aproval = WorkflowTransition(
        'request_aproval', title='Request Aproval',
        description='', category='',
        state_from=('created', 'author_action'),
        state_to='staff_action',
        permissions='qa scout owner'.split(),
    )
    request_review = WorkflowTransition(
        'request_review', title='Request Review',
        description='', category='',
        state_from= 'staff_action',
        state_to='author_action',
        permissions='qa scout owner'.split(),
    )
    #aprove = WorkflowTransition(
        #'request_review', title='Request Review',
        #description='', category='',
        #state_from= 'staff_action',
        #state_to='author_action',
        #permissions='qa scout owner'.split(),
    #)




class Asset(Mixin, Base):
    version = None
    url = ''
    comments = ''

    _workflow = AssetWorkflow
    __tablename__ = "assets"


    title = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    asset_url = sa.Column(sa.String(2048), nullable=True)
    # It may be desirable to embed a thumbnail  of the image along the data
    # Do NOT use this to store full size images
    inline_image = sa.Column(sa.LargeBinary, nullable=True)
    version = sa.Column (sa.Integer, nullable=False, default=0)
    # Denormalized string with the name of the OWNER of
    # an asset under copyright law, disregarding whether he is a Briefy systems uer
    owner = sa.Column(sa.String(255), nullable=False)
    # Refers to a system user - reachable trohough microservices/redis
    author_id = sa.Column(sautils.UUIDType, nullable=True)

    job_id = sa.Column(sautils.UUIDType, nullable=True)
    job = orm.relationship("Job", back_populates="job")





