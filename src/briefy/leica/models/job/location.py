"""Briefy Leica OrderLocation model."""
from briefy.common.db.mixins import Address as AddressMixin
from briefy.common.db.mixins import ContactInfoMixin
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.job import workflows

import colander
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
        'additional_phone', 'fullname', 'formatted_address', 'info'
    ]

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'timezone', 'versions',
            'can_create_roles', 'can_view_roles', 'can_edit_roles', 'can_delete_roles',
            'can_list_roles', 'local_roles'
        ],
    }

    __listing_attributes__ = __summary_attributes__

    order_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('orders.id'),
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

    def to_dict(self):
        """Custom to_dict method."""
        data = super().to_dict()
        data['coordinates'] = self.coordinates
        return data
