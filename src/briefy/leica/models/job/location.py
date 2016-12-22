"""Briefy Leica Job location model."""
from briefy.common.db.mixins import Address as AddressMixin
from briefy.common.db.mixins import NameMixin
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.job import workflows

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class LocationContactInfoMixin(NameMixin):
    """A mixin to manage contact information for the order location."""

    email = sa.Column(sautils.types.EmailType(), nullable=True, unique=False)
    """Email of the contact person."""

    mobile = sa.Column(sautils.types.PhoneNumberType(), nullable=False, unique=False)
    """Mobile phone number of the contact person."""

    additional_phone = sa.Column(sautils.types.PhoneNumberType(), nullable=True, unique=False)
    """Additional phone number of the contact person."""


class JobLocation(LocationContactInfoMixin, AddressMixin,
                  mixins.LeicaMixin, mixins.VersionMixin, Base):
    """Order location model."""

    _workflow = workflows.JobLocationWorkflow

    __summary_attributes__ = [
        'id', 'country', 'locality', 'coordinates', 'email', 'mobile',
        'additional_phone', 'fullname',
    ]

    __listing_attributes__ = __summary_attributes__

    order_id = sa.Column(
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
    """Order ID.

    Reference to the Order this location is attached to.
    """
