"""A working location of a Professional."""
from briefy.common.db.mixins import Address
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.professional import workflows
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils import ChoiceType
from sqlalchemy_utils import UUIDType

import colander
import enum
import sqlalchemy as sa


class DistanceUnits(enum.Enum):
    """Distance units."""

    km = 'km'
    mi = 'mi'


class WorkingLocation(Address, mixins.LeicaMixin, Base):
    """A working location for a Professional."""

    _workflow = workflows.LocationWorkflow

    __summary_attributes__ = [
        'id', 'created_at', 'updated_at', 'state', 'timezone',
        'locality', 'country', 'coordinates', 'latlng', 'formatted_address', 'info'
    ]

    __listing_attributes__ = __summary_attributes__

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'type'
        ]
    }

    professional_id = sa.Column(
        UUIDType(),
        sa.ForeignKey('professionals.id'),
        index=True,
        unique=False,
        info={'colanderalchemy': {
            'title': 'Professional id',
            'validator': colander.uuid,
            'missing': colander.drop,
            'typ': colander.String}}
    )
    type = sa.Column(
        sa.String(50),
        nullable=False
    )

    # Range from the main address
    range = sa.Column(sa.Integer(), default=10)
    range_unit = sa.Column(ChoiceType(DistanceUnits, impl=sa.String(5)), default='km')

    __mapper_args__ = {
        'polymorphic_identity': 'working_location',
        'polymorphic_on': type
    }

    @declared_attr
    def __tablename__(self):
        """Define tablename."""
        return 'workinglocations'

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['coordinates'] = self.coordinates
        data['latlng'] = self.latlng
        return data


class MainWorkingLocation(WorkingLocation):
    """The main working location for a Professional."""

    __mapper_args__ = {
        'polymorphic_identity': 'main_working_location'
    }


class AdditionalWorkingLocation(WorkingLocation):
    """An additional working location for a Professional."""

    __mapper_args__ = {
        'polymorphic_identity': 'additional_working_location'
    }
