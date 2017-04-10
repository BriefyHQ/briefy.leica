"""Billing information for a customer."""
from briefy.leica.models.billing_info import BillingInfo
from briefy.leica.models.billing_info import workflows
from briefy.leica.vocabularies import TaxIdStatusCustomers
from sqlalchemy import orm
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class CustomerBillingInfo(BillingInfo):
    """Billing information for a Professional."""

    __tablename__ = 'customer_billing_infos'
    _workflow = workflows.CustomerBillingInfoWorkflow

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'type', 'customer'
        ]
    }

    __raw_acl__ = (
        ('create', ('g:briefy_bizdev', 'g:briefy_finance', 'g:system')),
        ('list', ('g:briefy', 'g:system')),
        ('view', ('g:briefy', 'g:system')),
        ('edit', ('g:briefy_bizdev', 'g:briefy_finance', 'g:system')),
        ('delete', ('g:briefy_finance', 'g:system')),
    )

    __summary_attributes__ = [
        'id', 'created_at', 'updated_at', 'state', 'billing_address',
        'slug', 'legal_name', 'email',
    ]

    __listing_attributes__ = __summary_attributes__

    id = sa.Column(
        UUIDType(),
        sa.ForeignKey('billing_infos.id'),
        index=True,
        unique=True,
        primary_key=True,
        info={'colanderalchemy': {
              'title': 'Billing Info id',
              'validator': colander.uuid,
              'missing': colander.drop,
              'typ': colander.String}}
    )

    customer_id = sa.Column(
        UUIDType(),
        sa.ForeignKey('customers.id'),
        index=True,
        unique=True,
        info={
            'colanderalchemy': {
                'title': 'Customer id',
                'validator': colander.uuid,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )

    customer = orm.relationship('Customer')

    tax_id_status = sa.Column(
        sautils.ChoiceType(TaxIdStatusCustomers, impl=sa.String(3)),
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Tax ID Status',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Tax ID Status.

    Internal codes used by Finance to determine tax rates to be applied to this customer.
    """

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['customer'] = self.customer.to_summary_dict()
        return data