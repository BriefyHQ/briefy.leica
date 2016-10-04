"""Briefy Leica Project model."""
from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import BriefyRoles
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows
from briefy.ws.utils.user import add_user_info_to_state_history
from briefy.ws.utils.user import get_public_user_info
from zope.interface import Interface
from zope.interface import implementer

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class IProject(Interface):
    """Marker interface for Job"""


@implementer(IProject)
class Project(BriefyRoles, BaseMetadata, Mixin, Base):
    """Project model."""
    version = None

    __tablename__ = "projects"
    __session__ = Session
    _workflow = workflows.ProjectWorkflow

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', 'customer']}
    customer_id = sa.Column(sautils.UUIDType,
                            sa.ForeignKey('customers.id'),
                            nullable=False,
                            info={'colanderalchemy': {
                               'title': 'Customer',
                               'validator': colander.uuid,
                               'typ': colander.String}}
                            )
    customer = sa.orm.relationship('Customer', back_populates='projects')

    external_id = sa.Column(sa.String,
                            nullable=True,
                            info={'colanderalchemy': {
                                'title': 'External ID',
                                'missing': colander.drop}}
                            )

    """
    {
    "dimensions": {"value": "3000x2000", "operator": "ge"},
    "ratio": {"value": "4/3", "operator": "equal"},
    "size": {"value": "4000000", "operator": "le"},
    }

    """
    tech_requirements = sa.Column(sautils.JSONType,
                                  info={'colanderalchemy': {
                                       'title': 'Required Resolution',
                                       'missing': colander.drop,
                                       'typ': colander.String}}
                                  )

    jobs = sa.orm.relationship('Job', back_populates='project')

    brief = sa.Column(sautils.URLType,
                      nullable=True,
                      info={'colanderalchemy': {
                          'title': 'Brief link',
                          'validator': colander.url,
                          'missing': colander.drop,
                          'typ': colander.String}}
                      )

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        add_user_info_to_state_history(self.state_history)
        # TODO: improve this to be a function
        data['qa_manager'] = get_public_user_info(self.qa_manager)
        data['project_manager'] = get_public_user_info(self.project_manager)
        data['scout_manager'] = get_public_user_info(self.scout_manager)
        data['finance_manager'] = get_public_user_info(self.finance_manager)
        return data
