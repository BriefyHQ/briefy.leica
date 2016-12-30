"""Briefy Leica Project model."""
from briefy.common.db.mixins import BriefyRoles
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.project import workflows
from briefy.ws.utils.user import add_user_info_to_state_history
from sqlalchemy import orm
from zope.interface import Interface
from zope.interface import implementer

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class IProject(Interface):
    """Marker interface for Job."""


class CommercialInfoMixin(mixins.ProfessionalPayoutInfo, mixins.ProjectBriefyRoles,
                          mixins.OrderFinancialInfo):
    """Commercial details about a project."""

    contract = sa.Column(
        sautils.URLType,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Contract',
                'validator': colander.url,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Path to contract."""


@implementer(IProject)
class Project(CommercialInfoMixin, BriefyRoles, mixins.KLeicaVersionedMixin, Base):
    """A Project in Briefy."""

    _workflow = workflows.ProjectWorkflow

    __summary_attributes__ = [
        'id', 'title', 'description', 'created_at', 'updated_at', 'state', 'external_id'
    ]

    __summary_attributes_relations__ = ['customer']

    __listing_attributes__ = [
        'id', 'title', 'description', 'created_at', 'updated_at', 'state',
        'external_id', 'total_jobs'
    ]

    __raw_acl__ = (
        ('list', ('g:briefy_qa', 'g:briefy_pm', 'g:system')),
        ('view', ()),
        ('edit', ()),
        ('delete', ()),
    )

    __colanderalchemy_config__ = {'excludes': [
        'state_history', 'state', 'customer', '_customer_user', '_project_manager'
    ]}

    customer_id = sa.Column(sautils.UUIDType,
                            sa.ForeignKey('customers.id'),
                            nullable=False,
                            info={'colanderalchemy': {
                               'title': 'Customer',
                               'validator': colander.uuid,
                               'typ': colander.String}}
                            )
    """Customer ID.

    Builds the relation with :class:`briefy.leica.models.customer.Customer`.
    """

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
    """Technical requirements for jobs in this project.

    It stores a dictionary of requirements to be fullfiled by each asset of each Job.
    """

    cancellation_window = sa.Column(sa.Integer, default=0)
    """Period, in hours, before the shooting, a Job can be cancelled.

    i.e.: 24 would mean a Job in this project could be cancelled with at least 24 hour notice.
    Zero means no cancellation is possible.
    """

    availability_window = sa.Column(sa.Integer, default=0)
    """Period, in days, an availability date can be inputed.

    i.e.: 10 would mean a Job would have availability dates for, at least, 10 days in the future.
    Zero means no check is done.
    """

    approval_window = sa.Column(sa.Integer, default=0)
    """Period, in days, after the delivery, a Job could be approved or rejected by the customer.

    i.e.: 10 would mean a Job in this project could be approved up to 10 days after its delivery.
    Zero means a Job will be automatically approved.
    """

    jobs = orm.relationship(
        'JobOrder',
        backref=orm.backref('project'),
        lazy='dynamic'
    )
    """List of Jobs of this project.

    Returns a collection of :class:`briefy.leica.models.job.order.JobOrder`.
    """

    @sautils.aggregated('jobs', sa.Column(sa.Integer, default=0))
    def total_jobs(self):
        """Total jobs in this project.

        This attribute uses the Aggregated funcion of SQLAlchemy Utils, meaning the column
        should be updated on each change on any contained Job.
        """
        return sa.func.count('1')

    # Formerly know as brief
    briefing = sa.Column(
        sautils.URLType,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Briefing link',
                'validator': colander.url,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Path to briefing file regarding this Project."""

    release_template = sa.Column(
        sautils.URLType,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Release template',
                'validator': colander.url,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Path to release template file."""

    def to_listing_dict(self) -> dict:
        """Return a summarized version of the dict representation of this Class.

        Used to serialize this object within a parent object serialization.
        :returns: Dictionary with fields and values used by this Class
        """
        data = super().to_listing_dict()
        data = self._apply_actors_info(data)
        return data

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['slug'] = self.slug
        data = self._apply_actors_info(data)
        add_user_info_to_state_history(self.state_history)
        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data
