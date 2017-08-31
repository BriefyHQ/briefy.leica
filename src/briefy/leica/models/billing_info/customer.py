"""Billing information for a customer."""
from briefy.common.db.comparator import BaseComparator
from briefy.leica.models.billing_info import BillingInfo
from briefy.leica.models.billing_info import workflows
from briefy.leica.vocabularies import TaxIdStatusCustomers
from sqlalchemy import orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class LegalNameComparator(BaseComparator):
    """Customized comparator to lookup in the country key inside the billing_address json field."""

    def operate(self, op, other, escape=None):
        """Custom operate method."""
        def transform(q):
            """Transform the query applying a filter."""
            cls = self.__clause_element__()
            q = q.join(cls).filter(op(BillingInfo.title, other))
            return q

        return transform


class CustomerBillingInfo(BillingInfo):
    """Billing information for a Professional."""

    __tablename__ = 'customer_billing_infos'
    _workflow = workflows.CustomerBillingInfoWorkflow

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'type', 'customer'
        ]
    }

    __exclude_attributes__ = ['customer']

    __raw_acl__ = (
        ('create', ('g:briefy_bizdev', 'g:briefy_finance', 'g:system')),
        ('list', ('g:briefy', 'g:system')),
        ('view', ('g:briefy', 'g:system')),
        ('edit', ('g:briefy_bizdev', 'g:briefy_finance', 'g:system')),
        ('delete', ('g:briefy_finance', 'g:system')),
    )

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

    @hybrid_property
    def legal_name(self) -> str:
        """Company legal name.

        :return: legal name from title.
        """
        return self.title

    @legal_name.comparator
    def legal_name(cls) -> LegalNameComparator:
        """Billing address legal_name comparator.

        :return: _title class attribute.
        """
        return LegalNameComparator(cls)
