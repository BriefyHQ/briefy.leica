"""Contact Information for Users."""
import colander


class MessengerApps(colander.Mapping):
    """Messenger Apps info."""

    skype = colander.SchemaNode(
        colander.String(),
        missing='',
    )

    hangout = colander.SchemaNode(
        colander.String(),
        missing='',
        validator=colander.Email(),
    )

    whatsapp = colander.SchemaNode(
        colander.String(),
        missing=''
    )

    telegram = colander.SchemaNode(
        colander.String(),
        missing=''
    )
