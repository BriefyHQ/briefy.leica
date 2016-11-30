"""Briefy Leica Project model."""
from briefy.common.db.mixins import BriefyRoles
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.project import workflows
from briefy.ws.utils.user import add_user_info_to_state_history
from briefy.ws.utils.user import get_public_user_info
from sqlalchemy import orm
from zope.interface import Interface
from zope.interface import implementer

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class IProject(Interface):
    """Marker interface for Job"""


@implementer(IProject)
class Project(BriefyRoles, mixins.KLeicaVersionedMixin, Base):
    """A Project in Briefy."""

    _workflow = workflows.ProjectWorkflow

    __summary_attributes__ = [
        'id', 'title', 'description', 'created_at', 'updated_at', 'state', 'external_id'
    ]

    __listing_attributes__ = [
        'id', 'title', 'description', 'created_at', 'updated_at', 'state', 'external_id',
        'total_jobs'
    ]

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', 'customer']}

    customer_id = sa.Column(sautils.UUIDType,
                            sa.ForeignKey('customers.id'),
                            nullable=False,
                            info={'colanderalchemy': {
                               'title': 'Customer',
                               'validator': colander.uuid,
                               'typ': colander.String}}
                            )

    tech_requirements = sa.Column(
        sautils.JSONType,
        info={
            'colanderalchemy': {
                'title': 'Technical Requirements for this project.',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )

    jobs = orm.relationship(
        'Job',
        backref=orm.backref('project', lazy='joined'),
        lazy='dynamic'
    )

    @sautils.aggregated('jobs', sa.Column(sa.Integer, default=0))
    def total_jobs(self):
        """Total jobs in this project."""
        return sa.func.count('1')

    # Formely know as brief
    briefing = sa.Column(
        sautils.URLType,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Brief link',
                'validator': colander.url,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )

    def _apply_actors_info(self, data: dict) -> dict:
        """Apply actors information for a given data dictionary.

        :param data: Data dictionary.
        :return: Data dictionary.
        """
        actors = (
            ('qa_manager', 'qa_manager'),
            ('project_manager', 'project_manager'),
            ('scout_manager', 'scout_manager'),
            ('finance_manager', 'finance_manager'),
        )
        for key, attr in actors:
            data[key] = get_public_user_info(getattr(self, attr))

        return data

    def to_listing_dict(self) -> dict:
        """Return a summarized version of the dict representation of this Class.

        Used to serialize this object within a parent object serialization.
        :returns: Dictionary with fields and values used by this Class
        """
        data = super().to_listing_dict()
        customer = self.customer
        data['customer'] = customer.to_summary_dict() if customer else None
        return data

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        add_user_info_to_state_history(self.state_history)
        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data
