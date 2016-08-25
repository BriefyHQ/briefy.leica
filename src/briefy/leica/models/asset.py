from .workflows import AssetWorkflow
from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins.optin import OptIn
from briefy.leica.db import Base
from briefy.leica.db import Session
from sqlalchemy import orm

import sqlalchemy as sa
import sqlalchemy_utils as sautils





class Asset(Mixin, Base):
    version = None
    url = ''
    comments = ''

    _workflow = AssetWorkflow

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





