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


class CommercialInfoMixin:
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

    # Set price
    price_currency = sa.Column(
        sautils.CurrencyType,
        default='EUR'
    )
    """Price currency.

    ISO4217 code for the currency to be used by customer to pay Briefy.
    """

    _price = sa.Column(
        'price',
        sa.Integer,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Set Price',
                'missing': None,
                'typ': colander.Integer
            }
        }
    )
    """Price to be paid, by the customer, for each job.

    Amount to be paid by the customer for each job.
    This value is expressed in cents.
    """

    @property
    def price(self) -> int:
        """Price of this job.

        :return: Return the price, in `.price_currency` cents, of this job
        """
        return self._price

    # Photographer Payout
    payout_currency = sa.Column(
        sautils.CurrencyType,
        default='EUR'
    )
    """Professional Payout currency.

    ISO4217 code for the currency to be used to payout the professional.
    """

    payout_value = sa.Column(
        sa.Integer,
        nullable=False,
        default=0,
        info={
            'colanderalchemy': {
                'title': 'Photographer Payout',
                'missing': None,
                'typ': colander.Integer
            }
        }
    )
    """Professional Payout value.

    How much the professional will be paid for each Job.
    This value is expressed in cents.
    """


@implementer(IProject)
class Project(CommercialInfoMixin, BriefyRoles, mixins.KLeicaVersionedMixin, Base):
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
        'Job',
        backref=orm.backref('project', lazy='joined'),
        lazy='dynamic'
    )
    """List of Jobs of this project.

    Returns a collection of :class:`briefy.leica.models.job.Job`.
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

    def _apply_actors_info(self, data: dict) -> dict:
        """Apply actors information for a given data dictionary.

        :param data: Data dictionary.
        :return: Data dictionary.
        """
        actors = (
            ('qa_manager', 'qa_manager'),
            ('project_manager', 'project_manager'),
            ('scout_manager', 'scout_manager'),
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
