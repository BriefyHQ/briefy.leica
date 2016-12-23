"""Briefy Leica Customer Contact information."""
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import NameMixin
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.customer import workflows
from briefy.leica.vocabularies import ContactTypes

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class CustomerContact(NameMixin, BaseMetadata, mixins.LeicaMixin, Base):
    """Customer contact."""

    _workflow = workflows.ContactWorkflow

    __summary_attributes__ = [
        'id', 'fullname', 'email', 'mobile', 'position',
        'created_at', 'updated_at', 'state'
    ]

    __listing_attributes__ = __summary_attributes__

    __colanderalchemy_config__ = {'excludes': ['state_history', 'state']}

    customer_id = sa.Column(
        sautils.UUIDType,
        sa.ForeignKey('customers.id'),
        nullable=False,
        info={
            'colanderalchemy': {
                'title': 'Customer ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
    )
    """Customer ID.

    Reference to the Customer this contact is attached to.
    """

    type = sa.Column(
        sautils.ChoiceType(ContactTypes, impl=sa.String()),
        default='business',
        nullable=False
    )
    """Contact type.

    This field define what type of contact this one is.
    Options come from :mod:`briefy.leica.vocabularies`.
    """

    position = sa.Column(sa.String(255), nullable=True, unique=False)
    """Position of the contact person on the customer."""

    email = sa.Column(sautils.types.EmailType(), nullable=True, unique=False)
    """Email of the contact person."""

    mobile = sa.Column(sautils.types.PhoneNumberType(), nullable=True, unique=False)
    """Mobile phone number of the contact person."""
