"""Briefy Leica Customer model."""
from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins import BaseMetadata
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows
from zope.interface import Interface
from zope.interface import implementer

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
