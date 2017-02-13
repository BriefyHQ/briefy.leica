"""Import JobPool from Knack to Leica."""
from briefy.leica.models import Pool
from briefy.leica.sync import ModelSync
from briefy.leica.sync.location import pycountry


class PoolSync(ModelSync):
    """Syncronize Pools."""

    model = Pool
    knack_model_name = 'JobPool'

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for project object."""
        result = super().get_payload(kobj, briefy_id)
        country_iso = pycountry.countries.indices['name'].get(kobj.country.pop())
        result.update(
            dict(
                title=kobj.group_name,
                description=kobj.group_name,
                external_id=kobj.id,
                country=country_iso.alpha_2,
            )
        )
        return result
