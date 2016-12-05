"""Briefy Leica Assignment to a Job."""
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.job import workflows

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class AssignmentFinancialInfo:
    """Assignment financial information."""

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

    How much the professional will be paid for this Job.
    This value is expressed in cents.
    """

    # Photographer Expenses
    travel_expenses = sa.Column(
        sa.Integer,
        nullable=False,
        default=0,
        info={
            'colanderalchemy': {
                'title': 'Travel Expenses',
                'missing': None,
                'typ': colander.Integer
            }
        }
    )
    """Travel expenses amount.

    Amount to be paid to the professional as travel expenses.
    This value is expressed in cents.
    """

    additional_compensation = sa.Column(
        sa.Integer,
        nullable=False,
        default=0,
        info={
            'colanderalchemy': {
                'title': 'Additional Compensation',
                'missing': None,
                'typ': colander.Integer
            }
        }
    )
    """Amount of additional (extra) compensation.

    Amount to be paid to the professional as additional compensation.
    This value is expressed in cents.
    """

    payable = sa.Column(
        sa.Boolean,
        nullable=False,
        default=True,
        info={
            'colanderalchemy': {
                'title': 'Is this Assignment Payable?',
                'missing': True,
                'typ': colander.Boolean
            }
        }
    )
    """Payout should be payable or not?.

    By default all assignments should be paid but there are exceptions to this when a customer
    rejects a Job and we have to reassign it to a new Professional.
    """

    @property
    def invoices(self) -> list:
        """Return invoices for this assignment.

        :returns: List of invoices for this Assignment.
        """
        invoices = []
        return invoices


class JobAssignment(AssignmentFinancialInfo, mixins.LeicaMixin, mixins.VersionMixin, Base):
    """Job Assignment to a Professional."""

    _workflow = workflows.AssignmentWorkflow

    job_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('jobs.id'),
        nullable=False,
        info={
            'colanderalchemy': {
                'title': 'Job ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
    )
    """Job ID.

    Relantionship to :class:`briefy.leica.models.job.Job`
    """

    professional_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('professionals.id'),
        nullable=False,
        info={
            'colanderalchemy': {
                'title': 'Professional ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
    )
    """Professional ID.

    Relantionship to :class:`briefy.leica.models.professional.Professional`
    """

    @property
    def assets(self):
        """Assets from this JobAssignement.

        Collection of :class:`briefy.leica.models.asset.Asset`.
        """
        from briefy.leica.models.asset import Asset
        query = Asset.query().filter(
            sa.and_(
                Asset.job_id == self.job_id,
                Asset.professional_id == self.professional_id
            )
        )
        return query
