"""Briefy Leica OrderLocation model."""
from briefy.common.config import IMPORT_KNACK
from briefy.common.db.mixins import Address as AddressMixin
from briefy.common.db.mixins import ContactInfoMixin
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.job import workflows
from briefy.leica.utils.timezone import timezone_from_coordinates

import colander
import json
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class OrderLocation(ContactInfoMixin, AddressMixin,
                    mixins.LeicaMixin, mixins.VersionMixin, Base):
    """Order location model."""

    _workflow = workflows.OrderLocationWorkflow

    __versioned__ = {
        'exclude': ['state_history', '_state_history', 'timezone', ]
    }

    __summary_attributes__ = [
        'id', 'country', 'locality', 'coordinates', 'email', 'mobile',
        'additional_phone', 'fullname', 'first_name', 'last_name',
        'formatted_address', 'info'
    ]

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'timezone', 'versions',
            'can_create_roles', 'can_view_roles', 'can_edit_roles', 'can_delete_roles',
            'can_list_roles', 'local_roles', 'assignments'
        ],
        'overrides': {
            'mobile': {
                'title': 'Mobile phone number',
                'default': '',
                'missing': colander.drop,
                'typ': colander.String
            },
        }
    }

    __listing_attributes__ = __summary_attributes__

    order_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('orders.id'),
        index=True,
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

    @sautils.observes('_coordinates')
    def _update_timezone(self, _coordinates):
        """Update timezone when coordinates change."""
        # avoid update timezone when import data
        if IMPORT_KNACK:
            return

        lat = None
        lng = None
        value = json.loads(_coordinates)
        point = value.get('coordinates', None) if value else None
        if point:
            lng, lat = point

        if lat and lng:
            self.timezone = timezone_from_coordinates(lat, lng)

    def to_dict(self):
        """Custom to_dict method."""
        data = super().to_dict()
        data['coordinates'] = self.coordinates
        return data
