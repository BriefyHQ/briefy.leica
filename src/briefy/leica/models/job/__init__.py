"""Briefy Leica Job model."""
from briefy.common.db.mixins import BriefyRoles
from briefy.common.db.types import AwareDateTime
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.job import workflows
from briefy.leica.utils.transitions import get_transition_date
from briefy.ws.utils.user import add_user_info_to_state_history
from briefy.ws.utils.user import get_public_user_info
from datetime import datetime
from sqlalchemy import orm
from sqlalchemy.ext.hybrid import hybrid_property
from zope.interface import implementer
from zope.interface import Interface

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


__summary_attributes__ = [
    'id', 'title', 'description', 'created_at', 'updated_at', 'state',
    'approvable', 'total_assets', 'total_approvable_assets'
]

__listing_attributes__ = __summary_attributes__


class IJob(Interface):
    """Marker interface for Job"""


class JobAssignmentDates:
    """Mixin providing date-related information of a JobAssignment."""

    scheduled_datetime = sa.Column(
        AwareDateTime(),
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Scheduled date for shooting',
                'missing': colander.drop,
                'typ': colander.DateTime
            }
        }
    )
    """Scheduled date time of shooting."""

    # Relevant dates
    @hybrid_property
    def assignment_date(self) -> datetime:
        """Return last assignment date for this job.

        Information will be extracted from state history field.
        """
        transitions = ('assign', 'self_assign', )
        return get_transition_date(transitions, self)

    @hybrid_property
    def last_approval_date(self) -> datetime:
        """Return last QA transition date for this job.

        Information will be extracted from state history field.
        """
        transitions = ('approve', 'reject', )
        return get_transition_date(transitions, self)

    @hybrid_property
    def submission_date(self) -> datetime:
        """Return last submission date date for this job.

        Information will be extracted from state history field.
        """
        transitions = ('ready_for_upload', )
        return get_transition_date(transitions, self, first=True)


@implementer(IJob)
class JobAssignment(JobAssignmentDates, BriefyRoles, mixins.AssignmentFinancialInfo,
                    mixins.LeicaMixin, mixins.VersionMixin, Base):
    """A Job within a Project."""

    _workflow = workflows.JobWorkflow

    __summary_attributes__ = __summary_attributes__
    __listing_attributes__ = __listing_attributes__

    __raw_acl__ = (
        ('list', ('g:briefy_qa', 'g:briefy_pm', 'g:system')),
        ('view', ()),
        ('edit', ()),
        ('delete', ()),
    )

    __actors__ = (
        'professional_id',
        'project_manager',
        'scout_manager',
        'qa_manager',
    )

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'order', 'comments', 'professional', 'assets',
        ]
    }

    order_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('joborders.id'),
        nullable=False,
        info={
            'colanderalchemy': {
                'title': 'Job Order ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
    )
    """Job Order ID.

    Relantionship to :class:`briefy.leica.models.job.order.JobOrder`
    """

    # Professional
    professional_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('professionals.id'),
        nullable=True,
        info={'colanderalchemy': {
            'title': 'Professional ID',
            'validator': colander.uuid,
            'missing': colander.drop,
            'typ': colander.String}}
    )
    """Professional ID.

    Relationship with :class:`briefy.leica.models.professional.Professional`.

    This will be deprecated as soon as Assignments is implemented
    """

    # Assets for this job
    assets = orm.relationship(
        'Asset',
        backref=orm.backref('job', lazy='joined'),
        lazy='dynamic'
    )
    """Assets connected to this job.

    Collection of :class:`briefy.leica.models.asset.Asset`.
    """

    approvable_assets = orm.relationship(
        'Asset',
        primaryjoin='''and_(
            Asset.job_id == JobAssignment.id,
            Asset.state.in_(('approved', 'pending', 'delivered'))
        )''',
        viewonly=True

    )
    """Approvable assets connected to this job.

    To be listed here, an Asset, needs to be on one of the following states:

        * approved

        * pending

        * delivered

    Collection of :class:`briefy.leica.models.asset.Asset`.
    """

    comments = orm.relationship(
        'Comment',
        foreign_keys='Comment.entity_id',
        order_by='asc(Comment.created_at)',
        primaryjoin='Comment.entity_id == JobAssignment.id',
        lazy='dynamic'
    )
    """Comments connected to this job.

    Collection of :class:`briefy.leica.models.comment.Comment`.
    """

    submission_path = sa.Column(
        sautils.URLType,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Path to photographer submission',
                'validator': colander.url,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Path to the assets submission.

    On Knack it usually pointed to a google-drive folder where
    the Professional have write-permission.
    This will be deprecated when assets upload is handled also using Leica.
    """

    @sautils.aggregated('assets', sa.Column(sa.Integer, default=0))
    def total_assets(self):
        """Total number of assets.

        Counter of the number of assets in this Job.
        """
        return sa.func.count('1')

    @sautils.aggregated('approvable_assets', sa.Column(sa.Integer, default=0))
    def total_approvable_assets(self):
        """Total number of assets that can be approved.

        Counter of the number of assets in this Job that can be approved.
        """
        return sa.func.count('1')

    @property
    def approvable(self) -> bool:
        """Check if this job could be approved.

        :returns: Boolean indicating if it is possible to approve this job.
        """
        approvable_assets_count = self.total_approvable_assets
        check_images = self.order.number_of_assets <= approvable_assets_count
        return check_images

    @property
    def title(self) -> str:
        """Return the title of the JobOrder."""
        return self.order.title

    @property
    def description(self) -> str:
        """Return the description of the JobOrder."""
        return self.order.description

    @property
    def briefing(self) -> str:
        """Return the briefing URL for the parent project."""
        return self.order.project.briefing

    @property
    def assigned(self) -> bool:
        """Return if this job is assigned or not."""
        return True if (self.assignment_date and self.professional_id) else False

    def _apply_actors_info(self, data: dict) -> dict:
        """Apply actors information for a given data dictionary.

        :param data: Data dictionary.
        :return: Data dictionary.
        """
        actors = [(k, k) for k in self.__actors__]
        info = self._actors_info()
        for key, attr in actors:
            key = key if key != 'professional_id' else 'professional'
            try:
                value = info.get(attr).pop()
            except (AttributeError, IndexError):
                data[key] = None
            else:
                data[key] = get_public_user_info(value) if value else None
        return data

    def _summarize_relationships(self) -> dict:
        """Summarize relationship information.

        :return: Dictionary with summarized info for relationships.
        """
        data = {}
        project = self.order.project
        comments = self.comments
        locations = self.order.locations
        to_summarize = [
            ('project', project),
            ('comments', comments),
            ('locations', locations),
        ]
        if project:
            to_summarize.append(('customer', project.customer))

        for k, obj in to_summarize:
            if isinstance(obj, Base):
                serialized = obj.to_summary_dict() if obj else None
            else:
                serialized = [o.to_summary_dict() for o in obj]
            data[k] = serialized
        return data

    def to_listing_dict(self) -> dict:
        """Return a summarized version of the dict representation of this Class.

        Used to serialize this object within a parent object serialization.
        :returns: Dictionary with fields and values used by this Class
        """
        data = super().to_listing_dict()
        data.update(self._summarize_relationships())
        data = self._apply_actors_info(data)
        return data

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['title'] = self.title
        data['description'] = self.description
        data['briefing'] = self.briefing
        data['assignment_date'] = self.assignment_date

        data.update(self._summarize_relationships())

        # Workflow history
        add_user_info_to_state_history(self.state_history)

        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data
