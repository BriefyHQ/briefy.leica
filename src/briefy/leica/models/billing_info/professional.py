"""Billing information for a professional."""
from briefy.leica.models.billing_info import BillingInfo
from briefy.leica.models.billing_info import workflows
from briefy.leica.vocabularies import TaxIdStatusProfessionals
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class ProfessionalBillingInfo(BillingInfo):
    """Billing information for a Professional."""

    __tablename__ = 'professional_billing_infos'
    _workflow = workflows.ProfessionalBillingInfoWorkflow

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'type', 'professional'
        ]
    }

    __raw_acl__ = (
        ('create', ('g:briefy_scout', 'g:briefy_finance', 'g:system')),
        ('list', ('g:briefy', 'g:system')),
        ('view', ('g:briefy', 'g:system')),
        ('edit', ('g:briefy_scout', 'g:briefy_finance', 'g:system')),
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

    professional_id = sa.Column(
        UUIDType(),
        sa.ForeignKey('professionals.id'),
        index=True,
        unique=True,
        info={
            'colanderalchemy': {
                'title': 'Professional id',
                'validator': colander.uuid,
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )

    professional = orm.relationship('Professional')

    tax_id_status = sa.Column(
        sautils.ChoiceType(TaxIdStatusProfessionals, impl=sa.String(3)),
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

    _payment_info = sa.Column(
        'payment_info',
        JSONB,
        info={
            'colanderalchemy': {
                'title': 'Payment information',
                'missing': colander.drop,
                'typ': colander.List
            }
        }
    )
    """Payment information used for this professional."""

    @hybrid_property
    def payment_info(self) -> list:
        """Return list of payment information."""
        info = self._payment_info
        info = info if info else []
        return info

    @payment_info.setter
    def payment_info(self, value: list):
        """Set payment information for a professional."""
        self._payment_info = value

    @hybrid_property
    def default_payment_method(self) -> str:
        """Return the type of the preferred payment method used."""
        method_name = ''
        info = self.payment_info
        if info and len(info) > 0:
            method_name = info[0].get('type_')
        return method_name

    @hybrid_property
    def secondary_payment_method(self) -> str:
        """Return the type of the payment method used."""
        method_name = ''
        info = self.payment_info
        if info and len(info) > 1:
            method_name = info[1].get('type_')
        return method_name

    def to_dict(self, excludes: list=None, includes: list=None) -> dict:
        """Return a dictionary with fields and values used by this Class.

        :param excludes: attributes to exclude from dict representation.
        :param includes: attributes to include from dict representation.
        :returns: Dictionary with fields and values used by this Class
        """
        data = super().to_dict(excludes, includes)
        data['payment_info'] = self.payment_info
        data['default_payment_method'] = self.default_payment_method
        data['secondary_payment_method'] = self.secondary_payment_method
        data['professional'] = self.professional.to_summary_dict()
        return data
