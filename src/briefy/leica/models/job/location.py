"""Briefy Leica Job location model."""
from briefy.common.db.mixins import Address as AddressMixin
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.job import workflows

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class LocationContactInfoMixin:
    """A mixin to manage contact information of a professional."""

    contact = sa.Column(sa.String(255), nullable=True, unique=False)
    """Name of the contact person at the location.

    Fullname of the person that will receive the professional at the Job Location.
    """

    email = sa.Column(sa.String(255), nullable=True, unique=False)
    """Email of the contact person."""

    mobile = sa.Column(sa.String(255), nullable=True, unique=False)
    """Mobile phone number of the contact person."""


class JobLocation(LocationContactInfoMixin, AddressMixin, mixins.LeicaMixin, Base):
    """Job location model."""

    _workflow = workflows.JobWorkflow

    __summary_attributes__ = [
        'id', 'country', 'locality', 'coordinates'
    ]

    __listing_attributes__ = __summary_attributes__

    job_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('joborders.id'),
        nullable=False,
        info={
            'colanderalchemy': {
                'title': 'ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
    )
    """Job ID.

    Reference to the Job this location is attached to.
    """
