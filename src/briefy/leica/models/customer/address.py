"""Billing address for a Customer."""
from briefy.common.db.mixins import Address
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.customer import workflows
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa


class CustomerBillingAddress(Address, mixins.LeicaMixin, Base):
    """A Billing Information for a Customer."""

    _workflow = workflows.BillingAddressWorkflow

    customer_id = sa.Column(
        UUIDType(binary=False),
        sa.ForeignKey('customers.id'), unique=False,
        info={'colanderalchemy': {
            'title': 'Customer id',
            'validator': colander.uuid,
            'missing': colander.drop,
            'typ': colander.String}}
    )
    """Customer ID.

    Relationship with :class:`briefy.leica.models.customer.Customer`.
    """

    @declared_attr
    def __tablename__(self):
        """Define tablename."""
        return 'customerbillingaddresses'