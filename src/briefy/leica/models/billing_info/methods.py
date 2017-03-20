"""Payment methods."""
import colander


class PaymentMethod(colander.MappingSchema):
    """Information about a Payment Method."""

    type_ = colander.SchemaNode(
        colander.String()
    )


class PayPal(PaymentMethod):
    """PayPal payment method."""

    type_ = colander.SchemaNode(
        colander.String(),
        default='paypal'
    )

    email = colander.SchemaNode(
        colander.String(),
        validator=colander.Email(),
    )


class Skrill(PaymentMethod):
    """Skrill payment method."""

    type_ = colander.SchemaNode(
        colander.String(),
        default='skrill'
    )

    email = colander.SchemaNode(
        colander.String(),
        validator=colander.Email(),
    )


class BankAccount(PaymentMethod):
    """BankAccount payment method."""

    type_ = colander.SchemaNode(
        colander.String(),
        default='bank_account'
    )
    holder_name = colander.SchemaNode(
        colander.String()
    )
    iban = colander.SchemaNode(
        colander.String()
    )
    account_number = colander.SchemaNode(
        colander.String()
    )
    swift = colander.SchemaNode(
        colander.String(),
        missing=''
    )
    bank_name = colander.SchemaNode(
        colander.String()
    )
    bank_street_address = colander.SchemaNode(
        colander.String()
    )
    bank_city = colander.SchemaNode(
        colander.String()
    )
    bank_country = colander.SchemaNode(
        colander.String()
    )
