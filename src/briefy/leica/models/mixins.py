"""Briefy Leica mixins."""
import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class InternalRoles:
    """Internal roles for this job."""

    finance_manager = sa.Column(sautils.UUIDType,
                                nullable=True,
                                info={'colanderalchemy': {
                                    'title': 'Finance Manager ID',
                                    'validator': colander.uuid,
                                    'missing': None,
                                    'typ': colander.String}}
                                )

    qa_manager = sa.Column(sautils.UUIDType,
                           nullable=True,
                           info={'colanderalchemy': {
                               'title': 'QA Manager ID',
                               'validator': colander.uuid,
                               'missing': None,
                               'typ': colander.String}}
                           )

    scouting_manager = sa.Column(sautils.UUIDType,
                                 nullable=True,
                                 info={'colanderalchemy': {
                                     'title': 'Scouting Manager ID',
                                     'validator': colander.uuid,
                                     'missing': None,
                                     'typ': colander.String}}
                                 )


class FinancialInfo:
    """Mixin containing financial information."""

    payout_currency = sa.Column(sautils.CurrencyType, default='EUR')
    payout_value = sa.Column(sa.Integer,
                             nullable=True,
                             info={'colanderalchemy': {
                                   'title': 'Price',
                                   'missing': None,
                                   'typ': colander.Integer}}
                             )

    _price = sa.Column(
        'price',
        sa.Integer,
        nullable=True,
        info={'colanderalchemy': {
            'title': 'Set Price',
            'missing': None,
            'typ': colander.Integer}}
        )

    travel_expenses = sa.Column(sa.Integer,
                                nullable=True,
                                info={'colanderalchemy': {
                                    'title': 'Travel Expenses',
                                    'missing': None,
                                    'typ': colander.Integer}}
                                )

    @property
    def price(self) -> int:
        """Price of this job.

        :return: Return the price, in cents, of this job.
        """
        return self._price
