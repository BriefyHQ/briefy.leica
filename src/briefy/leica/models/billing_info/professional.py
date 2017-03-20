"""Billing information for a professional."""
from briefy.common.utils import schema
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.models.billing_info import workflows
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class ProfessionalBillingInfo(
    mixins.TaxInfo, mixins.BillingAddress, mixins.LeicaVersionedMixin, Base
):
    """Billing information for a Professional."""

    _workflow = workflows.ProfessionalBillingInfoWorkflow

    __raw_acl__ = (
        ('create', ('g:briefy_scout', 'g:briefy_finance', 'g:system')),
        ('list', ('g:briefy', 'g:system')),
        ('view', ('g:briefy', 'g:system')),
        ('edit', ('g:briefy_scout', 'g:briefy_finance', 'g:system')),
        ('delete', ('g:briefy_finance', 'g:system')),
    )

    __summary_attributes__ = [
        'id', 'created_at', 'updated_at', 'state',
        'locality', 'country', 'formatted_address', 'info',
        'slug', 'legal_name', 'email', 'primary_payment_method', 'secondary_payment_method'
    ]

    __listing_attributes__ = __summary_attributes__

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state'
        ]
    }

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

    legal_name = sa.Column(
        sa.String(255),
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Company Legal name',
                'missing': '',
                'typ': colander.String
            }
        }
    )
    """Legal name of the company.

    i.e.: Insta Stock GmbH
    """

    first_name = sa.Column(
        sa.String(255),
        index=True,
        nullable=False,
        unique=False,
        info={
            'colanderalchemy': {
                'title': 'Creative First Name',
                'typ': colander.String
            }
        }
    )
    """First name of a person."""

    last_name = sa.Column(
        sa.String(255),
        index=True,
        nullable=False,
        unique=False,
        info={
            'colanderalchemy': {
                'title': 'Creative First Name',
                'typ': colander.String
            }
        }
    )
    """Last name of a person."""

    email = sa.Column(
        sautils.types.EmailType(),
        nullable=True,
        unique=True,
        info={
            'colanderalchemy': {
                'title': 'Email',
                'default': '',
                'typ': colander.String
            }
        }
    )
    """Email of the contact person."""

    primary_payment_info = sa.Column(
        'primary_payment_info',
        JSONB,
        info={
            'colanderalchemy': {
                'title': 'Primary payment method',
                'missing': colander.drop,
                'typ': schema.JSONType
            }
        }
    )
    """Primary payment method used for this professional."""

    @hybrid_property
    def primary_payment_method(self) -> str:
        """Return the type of the payment method used."""
        method_name = ''
        info = self.primary_payment_info
        if info:
            method_name = info.get('type_')
        return method_name

    secondary_payment_info = sa.Column(
        'secondary_payment_info',
        JSONB,
        info={
            'colanderalchemy': {
                'title': 'Secondary payment method',
                'missing': colander.drop,
                'typ': schema.JSONType
            }
        }
    )
    """Secondary payment method used for this professional."""

    @hybrid_property
    def secondary_payment_method(self) -> str:
        """Return the type of the payment method used."""
        method_name = ''
        info = self.secondary_payment_info
        if info:
            method_name = info.get('type_')
        return method_name

    @declared_attr
    def title(cls):
        """Return the User fullname."""
        return sa.orm.column_property(cls.first_name + " " + cls.last_name)

    @declared_attr
    def __tablename__(self):
        """Define tablename."""
        return 'professional_billing_infos'

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['slug'] = self.slug
        data['primary_payment_method'] = self.primary_payment_method
        data['secondary_payment_method'] = self.secondary_payment_method
        return data
