"""Briefy Leica Job model."""
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import BriefyRoles
from briefy.common.db.mixins import Mixin
from briefy.common.db.types import AwareDateTime
from briefy.common.vocabularies.categories import CategoryChoices
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import workflows
from briefy.ws.utils.user import add_user_info_to_state_history
from briefy.ws.utils.user import get_public_user_info
from zope.interface import implementer
from zope.interface import Interface

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


__summary_attributes__ = [
    'id', 'title', 'description', 'created_at', 'updated_at', 'state', 'approvable',
    'number_of_photos', 'total_assets', 'total_approvable_assets'
]

__listing_attributes__ = __summary_attributes__


class IJob(Interface):
    """Marker interface for Job"""


@implementer(IJob)
class Job(BriefyRoles, Mixin, BaseMetadata, Base):
    """A Job within a project."""

    version = None

    _workflow = workflows.JobWorkflow
    __tablename__ = 'jobs'
    __session__ = Session

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
        'finance_manager',
        'scout_manager',
        'qa_manager',
    )

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state', 'project', 'comments',
                                               'internal_comments', 'professional']}

    project_id = sa.Column(sautils.UUIDType,
                           sa.ForeignKey('projects.id'),
                           nullable=False,
                           info={'colanderalchemy': {
                               'title': 'Project ID',
                               'validator': colander.uuid,
                               'missing': None,
                               'typ': colander.String}}
                           )

    project = sa.orm.relationship('Project', uselist=False, back_populates='jobs')

    # Professional
    professional_id = sa.Column(
        sautils.UUIDType,
        # sa.ForeignKey('professionals.id'),
        nullable=True,
        info={'colanderalchemy': {
            'title': 'Professional ID',
            'validator': colander.uuid,
            'missing': colander.drop,
            'typ': colander.String}}
    )
    # professional = sa.orm.relationship('Professional', back_populates='jobs')

    # Job details
    job_requirements = sa.Column(sa.Text, default='')
    job_locations = sa.orm.relationship('JobLocation')

    # Category of the job
    category = sa.Column(
        sautils.ChoiceType(CategoryChoices, impl=sa.String()),
        default='undefined',
        nullable=True
    )

    # Job Identifiers
    job_id = sa.Column(sa.String, nullable=False)  # Was internal_job_id
    customer_job_id = sa.Column(sa.String, default='')  # Id on the customer database

    assets = sa.orm.relationship('Asset', back_populates='job')
    comments = sa.orm.relationship('Comment',
                                   foreign_keys='Comment.entity_id',
                                   order_by='asc(Comment.created_at)',
                                   primaryjoin='Comment.entity_id == Job.id')
    internal_comments = sa.orm.relationship('InternalComment',
                                            foreign_keys='InternalComment.entity_id',
                                            order_by='asc(InternalComment.created_at)',
                                            primaryjoin='InternalComment.entity_id == Job.id')

    number_of_photos = sa.Column(sa.Integer(), default=20)

    _assignment_date = sa.Column(AwareDateTime(),
                                 nullable=True,
                                 info={'colanderalchemy': {
                                     'title': 'Assignment date',
                                     'missing': colander.drop,
                                     'typ': colander.DateTime}}
                                 )

    scheduled_datetime = sa.Column(
        AwareDateTime(),
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Assignment date',
                'missing': colander.drop,
                'typ': colander.DateTime
            }
        }
    )

    @property
    def total_assets(self) -> int:
        """Total number of assets.

        :returns: Number of assets on this job.
        """
        return len(self.assets)

    @property
    def total_approvable_assets(self) -> int:
        """Total number of assets.

        :returns: Number of assets on this job.
        """
        approvable_assets_count = len(
            [a for a in self.assets if a.state in ('pending', 'approved', 'delivered')]
        )
        return approvable_assets_count

    @property
    def approvable(self) -> bool:
        """Check if this job could be approved.

        :returns: Boolean indicating if it is possible to approve this job.
        """
        approvable_assets_count = self.total_approvable_assets
        check_images = self.number_of_photos <= approvable_assets_count
        return check_images

    @property
    def customer(self):
        """Customer hiring this job."""
        return self.project.customer.title

    @property
    def assignment_date(self):
        """Timestamp of when photographer was assigned to the job"""
        if self._assignment_date:
            return self._assignment_date
        # TODO: else: retrieve date from the workflow history
        return None

    @assignment_date.setter
    def assignment_date(self, value):
        """Explicitly sets an assignment datetime stamp.

           This will override any assignemnt datetime that
           might be infered from the workflow history
        """
        self._assignment_date = value

    @property
    def project_brief(self):
        """Returns the brief URL for the parent project"""
        return self.project.brief

    @property
    def external_status(self) -> str:
        """Status of this job to be displayed to the customer.

        :return: A friendly name for the workflow state.
        """
        # TODO: Use a mapping
        status = self.workflow.state.name
        return status

    # Job ID on knack
    external_id = sa.Column(sa.String,
                            nullable=True,
                            info={'colanderalchemy': {
                                  'title': 'External ID',
                                  'missing': colander.drop}}
                            )

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
            value = info.get(attr, None)
            data[key] = get_public_user_info(value) if value else None
        return data

    def _summarize_relationships(self) -> dict:
        """Summarize relationship information.

        :return: Dictionary with summarized info for relationships.
        """
        data = {}
        project = self.project
        comments = self.comments
        job_locations = self.job_locations
        to_summarize = [
            ('project', project),
            ('comments', comments),
            ('job_locations', job_locations),
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
        # data = self._apply_actors_info(data)
        return data

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict(excludes=['internal_comments'])
        data['description'] = self.description
        data['project_brief'] = self.project_brief
        data['assignment_date'] = self.assignment_date

        data.update(self._summarize_relationships())

        # Workflow history
        add_user_info_to_state_history(self.state_history)

        # Apply actor information to data
        data = self._apply_actors_info(data)
        return data
