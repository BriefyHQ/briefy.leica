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

    professional_id = sa.Column(
        UUIDType(binary=False), sa.ForeignKey('professionals.id'), unique=False,
        info={'colanderalchemy': {
            'title': 'Professional id',
            'validator': colander.uuid,
            'missing': colander.drop,
            'typ': colander.String}}
    )
    type = sa.Column(sa.String(50), nullable=False)

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
