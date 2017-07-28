"""Briefy Leica Lead model."""
from briefy.leica.events import leadorder as events
from briefy.leica.models.job import workflows
from briefy.leica.models.job.order import Order
from sqlalchemy.ext.associationproxy import association_proxy

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class LeadOrder(Order):
    """A Lead order from the customer."""

    __tablename__ = 'leadorders'

    _workflow = workflows.LeadOrderWorkflow

    _default_notify_events = {
        'POST': events.LeadOrderCreatedEvent,
        'PUT': events.LeadOrderUpdatedEvent,
        'GET': events.LeadOrderLoadedEvent,
        'DELETE': events.LeadOrderDeletedEvent,
    }

    id = sa.Column(
        sautils.UUIDType(),
        sa.ForeignKey('orders.id'),
        index=True,
        unique=True,
        primary_key=True,
        info={
            'colanderalchemy': {
                  'title': 'LeadOrder ID',
                  'validator': colander.uuid,
                  'missing': colander.drop,
                  'typ': colander.String
            }
        }
    )

    confirmation_fields = association_proxy('project', 'leadorder_confirmation_fields')
    """List of fields to be used in confirmation."""
