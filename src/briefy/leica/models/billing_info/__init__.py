"""Billing information for a professional."""
from briefy.leica.db import Base
from briefy.leica.models import mixins
from briefy.leica.vocabularies import TaxIdTypes
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

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

    first_name = sa.Column(
        sa.String(255),
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
        unique=False,
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

    @hybrid_property
    def title(self):
        """Return fullname as title."""
        return self.first_name + ' ' + self.last_name

    @title.setter
    def title(self, value: str):
        """Avoid set title since it is a computed field."""
        return ValueError(
            'You can not set the billing info title. Please update first_name and last_name.'
        )

    @title.expression
    def title(cls):
        """Return fullname as title."""
        return cls.first_name + ' ' + cls.last_name

    @sautils.observes('first_name', 'last_name')
    def _title_observer(self, first_name, last_name):
        """Calculate dates on a change of a state."""
        self._title = first_name + ' ' + last_name

    def to_dict(self, excludes: list=None, includes: list=None) -> dict:
        """Return a dictionary with fields and values used by this Class.

        :param excludes: attributes to exclude from dict representation.
        :param includes: attributes to include from dict representation.
        :returns: Dictionary with fields and values used by this Class
        """
        data = super().to_dict(excludes, includes)
        data['slug'] = self.slug
        data['title'] = self.title
        return data
