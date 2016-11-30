"""Briefy Leica Customer model."""
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.customer import workflows
from briefy.ws.utils.user import add_user_info_to_state_history
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from zope.interface import Interface
from zope.interface import implementer

import colander
import sqlalchemy as sa


class ICustomer(Interface):
    """Marker interface for a Customer"""


@implementer(ICustomer)
class Customer(mixins.KLeicaVersionedMixin, Base):
    """Customer model."""

    version = None

    _workflow = workflows.CustomerWorkflow

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', '_slug']}

    projects = sa.orm.relationship('Project', back_populates='customer')
    external_id = sa.Column(sa.String,
                            nullable=True,
                            info={'colanderalchemy': {
                                'title': 'External ID',
                                'missing': colander.drop}}
                            )

    projects = orm.relationship(
        'Project',
        backref=orm.backref('customer', lazy='joined'),
        lazy='dynamic'
    )

    jobs = orm.relationship(
        'Job',
        backref=orm.backref('customer', lazy='joined'),
        lazy='dynamic'
    )

    @declared_attr
    def _external_model_(cls):
        """Name of the model on Knack."""
        return 'Company'

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        add_user_info_to_state_history(self.state_history)
        return data

    def __repr__(self):
        return '<Customer-proxy \'{0}\'>'.format(self.title)
