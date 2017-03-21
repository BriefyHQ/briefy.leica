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
    # Only needed if first digit is 1 or 2
    iban = colander.SchemaNode(
        colander.String()
    )
    # Only needed if first digit 3
    account_number = colander.SchemaNode(
        colander.String()
    )
    # Only needed if first digit 3
    swift = colander.SchemaNode(
        colander.String(),
        missing=''
    )
    # Only needed if first digit 3
    bank_name = colander.SchemaNode(
        colander.String(),
        missing=''
    )
    # Only needed if first digit 3
    bank_street_address = colander.SchemaNode(
        colander.String(),
        missing=''
    )
    # Only needed if first digit 3
    bank_city = colander.SchemaNode(
        colander.String(),
        missing=''
    )
    # Only needed if first digit 3
    bank_country = colander.SchemaNode(
        colander.String(),
        missing=''
    )
