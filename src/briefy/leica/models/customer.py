"""Briefy Leica Customer model."""
from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins import BaseMetadata
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows
from briefy.ws.utils.user import add_user_info_to_state_history
from zope.interface import Interface
from zope.interface import implementer

import colander
import sqlalchemy as sa


class ICustomer(Interface):
    """Marker interface for a Customer"""


@implementer(ICustomer)
class Customer(BaseMetadata, Mixin, Base):
    """Customer model."""

    version = None

    __tablename__ = "customers"
    __session__ = Session
    _workflow = workflows.CustomerWorkflow

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', '_slug']}

    projects = sa.orm.relationship('Project', back_populates='customer')
    external_id = sa.Column(sa.String,
                            nullable=True,
                            info={'colanderalchemy': {
                                'title': 'External ID',
                                'missing': colander.drop}}
                            )

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        add_user_info_to_state_history(self.state_history)
        return data

    def __repr__(self):
        return '<Customer-proxy \'{0}\'>'.format(self.title)
