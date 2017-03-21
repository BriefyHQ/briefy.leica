"""Billing information for a professional."""
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.vocabularies import TaxIdTypes
from sqlalchemy.ext.declarative import declared_attr


import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class TaxInfo:
    """Tax information."""

    tax_id_type = sa.Column(
        sautils.ChoiceType(TaxIdTypes, impl=sa.String(3)),
        nullable=False,
        default='1',
        info={
            'colanderalchemy': {
                'title': 'Tax ID Type',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Tax ID type (Vocabulary is implemented in each subclass)."""

    tax_id = sa.Column(
        sa.String(50), nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Tax ID',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Tax ID for this customer.

    i.e.: 256.018.208-49
    """

    tax_id_name = sa.Column(
        sa.String(50), nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Tax ID type',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Tax ID Name.

    i.e.: CPF / VAT/ BTW
    """


class BillingInfo(TaxInfo, mixins.BillingAddress, mixins.LeicaVersionedMixin, Base):
    """Billing information."""

    __tablename__ = 'billing_infos'

    __colanderalchemy_config__ = {
        'excludes': [
            'state_history', 'state', 'type'
        ]
    }

    legal_name = sa.Column(
        'title',
        sa.String(255),
        nullable=True,
        default='',
        info={
            'colanderalchemy': {
                'title': 'Company Legal name',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Legal name of the company.

    i.e.: Insta Stock GmbH
    """

    email = sa.Column(
        sautils.types.EmailType(),
        nullable=True,
        unique=True,
        info={
            'colanderalchemy': {
                'title': 'Email',
                'missing': colander.drop,
                'default': '',
                'typ': colander.String
            }
        }
    )
    """Email to receive the invoices."""

    type = sa.Column(sa.String(50))
    """Polymorphic type."""

    @declared_attr
    def __mapper_args__(cls):
        """Return polymorphic identity."""
        cls_name = cls.__name__.lower()
        args = {
            'polymorphic_identity': cls_name,
        }
        if cls_name == 'billinginfo':
            args['polymorphic_on'] = cls.type
        return args

    def to_dict(self):
        """Return a dict representation of this object."""
        data = super().to_dict()
        data['slug'] = self.slug
        return data
