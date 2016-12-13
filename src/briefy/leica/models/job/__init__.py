"""Briefy Leica Job model."""
from briefy.common.db.mixins import BriefyRoles
from briefy.common.db.types import AwareDateTime
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.job import workflows
from briefy.leica.utils.transitions import get_transition_date
from briefy.leica.vocabularies import JobInputSource
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
    'id', 'title', 'description', 'created_at', 'updated_at', 'state', 'approvable',
    'number_of_assets', 'total_assets', 'total_approvable_assets'
]

__listing_attributes__ = __summary_attributes__


class IJob(Interface):
    """Marker interface for Job"""


class JobDates:
    """Mixin providing date-related information of a Job."""

    _availability = sa.Column(
        'availability',
        sautils.JSONType,
        info={
            'colanderalchemy': {
                'title': 'Availability for scheduling this job.',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Availability attribute.

    Access to it should be done using the hybrid_property availability.
    """

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

    @hybrid_property
    def availability(self) -> list:
        """Return availability for a Job.

        This should return a list with zero or more available dates for
        scheduling this job.
        i.e.::

            [
              datetime(2016, 12, 21, 12, 0, 0),
              datetime(2016, 12, 22, 14, 0, 0),
            ]

        """
        availability = self._availability
        if isinstance(availability, dict):
            availability = [availability, ]
        return availability

    @availability.setter
    def availability(self, value: dict):
        """Set availabilities for a job."""
        self._availability = value

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
        transitions = ('approve', 'reject', )
        return get_transition_date(transitions, self, first=True)


@implementer(IJob)
class Job(JobDates, BriefyRoles, mixins.JobFinancialInfo, mixins.KLeicaVersionedMixin, Base):
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
            'state_history', 'state', 'project', 'comments', 'customer', 'professional',
        ]
    }

    # Customer
    customer_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('customers.id'),
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Customer ID',
                'validator': colander.uuid,
                'missing': None,
                'typ': colander.String
            }
        }
    )
    """Customer ID.

    Relationship with :class:`briefy.leica.models.customer.Customer`.
    """

    # Project
    project_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('projects.id'),
        nullable=False,
        info={
            'colanderalchemy': {
                'title': 'Project ID',
                'validator': colander.uuid,
                'missing': None,
                'typ': colander.String
            }
        }
    )
    """Project ID.

    Relationship with :class:`briefy.leica.models.project.Project`.
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

    # Job details
    locations = orm.relationship(
        'JobLocation',
        backref=orm.backref('job', lazy='joined'),
        lazy='joined'
    )
    """Job Locations.

    Relationship with :class:`briefy.leica.models.job.location.JobLocation`.
    """

    # Job Assignments
    assignments = orm.relationship(
        'JobAssignment',
        backref=orm.backref('job', lazy='joined'),
        lazy='joined'
    )
    """Job Assignments.

    Relationship with :class:`briefy.leica.models.job.assignment.JobAssignment`.
    """

    requirements = sa.Column(sa.Text, default='')
    """Human-readable requirements for a Job."""

    number_of_assets = sa.Column(sa.Integer(), default=20)
    """Number of assets of a job."""

    category = sa.Column(
        sautils.ChoiceType(CategoryChoices, impl=sa.String()),
        default='undefined',
        nullable=True
    )
    """Category of this job.

    Options come from :mod:`briefy.common.vocabularies.categories`.
    """

    source = sa.Column(
        sautils.ChoiceType(JobInputSource, impl=sa.String()),
        default='briefy',
        nullable=False
    )
    """Source of this job.

    This field stores which part created this job, Customer or Briefy.
    Options come from :mod:`briefy.leica.vocabularies`.
    """
    # Job Identifiers
    job_id = sa.Column(sa.Integer, nullable=True, index=True)
    """Job ID was the main Briefy id for a Job.

    This field was used on Knack as an auto-incremented field named 'internal_job_id'.
    """
    customer_job_id = sa.Column(sa.String, default='', index=True)
    """ID of the job for the customer.

    Reference for the customer to find this job. On Knack this field was refered as 'job_id'.
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
            Asset.job_id == Job.id,
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
        primaryjoin='Comment.entity_id == Job.id',
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

    _delivery = sa.Column(
        'delivery',
        sautils.JSONType,
        info={
            'colanderalchemy': {
                'title': 'Delivery information.',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Delivery links.

    JSON with a collection of delivery links. Should be accessed using the 'delivery' attribute.
    """

    @hybrid_property
    def delivery(self) -> dict:
        """Return delivery info for a Job.

        This should return a dict with the delivery method and URL
        i.e.::

            {
                'sftp': 'sftp://agoda@delivery.briefy.co/bali/3456/',
                'gdrive': 'https://drive.google.com/foo/bar',
            }

        """
        delivery = self._delivery
        return delivery

    @delivery.setter
    def delivery(self, value: dict):
        """Set delivery information for a job."""
        self._delivery = value

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
        check_images = self.number_of_assets <= approvable_assets_count
        return check_images

    @property
    def briefing(self) -> str:
        """Return the briefing URL for the parent project."""
        return self.project.briefing

    @property
    def assigned(self) -> bool:
        """Return if this job is assigned or not."""
        return True if (self.assignment_date and self.professional_id) else False

    @property
    def tech_requirements(self) -> dict:
        """Tech requirements for this job.

        :return: A dictionary with technical requirements for a job.
        """
        project = self.project
        return project.tech_requirements

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
        project = self.project
        comments = self.comments
        locations = self.locations
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
        data = super().to_dict(excludes=['internal_comments'])
        data['description'] = self.description
        data['briefing'] = self.briefing
        data['assignment_date'] = self.assignment_date

        data.update(self._summarize_relationships())

        # Workflow history
        add_user_info_to_state_history(self.state_history)

        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data
