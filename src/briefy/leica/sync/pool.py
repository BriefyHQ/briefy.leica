"""Import JobPool from Knack to Leica."""
from briefy.leica import logger
from briefy.leica.models import Pool
from briefy.leica.models import Professional
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

    def add_photographers(self, obj, kobj) -> None:
        """Add all existing Photographers in the knack Pool to the leica db Pool.

        :param obj: db model Pool instance
        :param kobj: knack model Pool instance
        :return: None
        """
        for kuser in kobj.photographers:
            professional_id = self.rosetta.get(kuser['id'])
            professional = Professional.get(professional_id)
            if professional:
                obj.professionals.append(professional)
            else:
                msg = 'Professional not found: {professional_id}. Pool: {title}.'
                logger.debug(msg.format(professional_id=professional_id, title=obj.title))

    def add(self, kobj, briefy_id):
        """Add new Pool to database."""
        obj = super().add(kobj, briefy_id)
        self.add_photographers(obj, kobj)
        return obj
