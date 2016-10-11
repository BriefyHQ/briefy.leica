from briefy.leica.sync import ModelSync
from briefy.leica.models import Customer


class CustomerSync(ModelSync):
    """Syncronize Customers."""

    model = Customer
    knack_model_name = 'Company'

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for customer object."""
        result = super().get_payload(kobj, briefy_id)
        result.update(
            dict(
                external_id=kobj.id,
                title=kobj.company_name
            )
        )
        return result
