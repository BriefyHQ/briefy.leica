"""Import Professionals to Leica."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from briefy.common.utils.transformers import to_serializable
from briefy.leica import logger
from briefy.leica.models import AdditionalWorkingLocation
from briefy.leica.models import Facebook
from briefy.leica.models import FiveHundred
from briefy.leica.models import Flickr
from briefy.leica.models import GDrive
from briefy.leica.models import Linkedin
from briefy.leica.models import MainWorkingLocation
from briefy.leica.models import Photographer
from briefy.leica.models import Pool
from briefy.leica.models import Portfolio
from briefy.leica.sync import cleanse_phone_number
from briefy.leica.sync import ModelSync
from briefy.leica.sync import PLACEHOLDERS
from briefy.leica.sync.location import create_location_dict
from urllib.parse import urlparse


class PhotographerSync(ModelSync):
    """Syncronize Professionals."""

    model = Photographer
    knack_model_name = 'Photographer'

    def _state_history(self, state: str):
        """Create state history structure."""
        now = datetime_utcnow()
        created_at = to_serializable(now)
        updated_at = to_serializable(now)
        ACTOR = str(SystemUser.id)
        history = []
        history.append(
            {
                'date': created_at,
                'message': 'Imported professional from Knack database',
                'actor': ACTOR,
                'transition': '',
                'from': '',
                'to': 'created'
            },
        )
        history.append(
                {
                    'date': created_at,
                    'message': 'Automatic transition',
                    'actor': ACTOR,
                    'transition': 'submit',
                    'from': 'created',
                    'to': 'pending',
                },
        )
        history.append(
            {
                'date': updated_at,
                'message': 'Automatic transition',
                'actor': ACTOR,
                'transition': 'approve',
                'from': 'pending',
                'to': 'validation',
            },
        )
        history.append(
            {
                'date': updated_at,
                'message': 'Automatic transition',
                'actor': ACTOR,
                'transition': 'validate',
                'from': 'validation',
                'to': 'trial',
            },
        )
        if state in ('active', ):
            history.append(
                {
                    'date': updated_at,
                    'message': 'Automatic transition',
                    'actor': ACTOR,
                    'transition': 'activate',
                    'from': 'trial',
                    'to': 'active',
                },
            )
        elif state in ('trial', ):
            history.append(
                {
                    'date': updated_at,
                    'message': 'Automatic transition',
                    'actor': ACTOR,
                    'transition': 'inactivate',
                    'from': 'trial',
                    'to': 'inactive',
                },
            )

        return history

    def add_address(self, kobj, obj, location_model=None, field_name=''):
        """Add working location address from knack object."""
        location_dict = create_location_dict(field_name, kobj)
        if not location_dict:
            return

        try:
            location = location_model(**location_dict)
            self.session.add(location)
            self.session.flush()
        except Exception as error:
            msg = 'Failure to create location for Photographer: {name}. Error: {error}'
            logger.error(msg.format(customer=obj.first_name, error=error))
        else:
            obj.locations.append(location)

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for a Professional object."""
        result = super().get_payload(kobj, briefy_id)

        first_name = kobj.display_name.first or PLACEHOLDERS['first_name']
        last_name = kobj.display_name.last or PLACEHOLDERS['last_name']
        mobile = kobj.phone.get('number') if kobj.phone else None
        country = kobj.country if kobj.country else ''
        location = create_location_dict('working_location_1', kobj, country)
        if location and not country:
            country = location.get('country')

        if mobile:
            mobile = cleanse_phone_number(mobile, country, kobj)

        state = 'inactive' if kobj.blacklist else 'active'
        state_history = self._state_history(state)
        result.update(
            dict(
                external_id=kobj.id,
                state=state,
                state_history=state_history,
                email=kobj.email.email or PLACEHOLDERS['email'],
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                # TODO: this will be removed when update DB (title is now a computed value)
                title='{0} {1}'.format(first_name, last_name),
                owner=briefy_id,
                mobile=mobile
            )
        )
        return result

    def add_locations(self, kobj, obj):
        """Add all Photographer locations."""
        locations = ['working_location_1', 'working_location_2', 'working_location_3']
        model = MainWorkingLocation
        for i, location in enumerate(locations):
            value = getattr(kobj, location)
            if value:
                if i > 1:
                    model = AdditionalWorkingLocation
                self.add_address(kobj, obj,
                                 location_model=model,
                                 field_name=location)

    def add_professional_pool(self, obj, kobj) -> None:
        """Migrate JobPool for each Professional if exists.

        :param obj: db model Professional instance
        :param kobj: knack model Photographer instance
        :return: None
        """
        for kpool in kobj.job_pool:
            kpool_id = kpool['id']
            db_pool = Pool.query().filter_by(external_id=kpool_id).one_or_none()
            if db_pool:
                obj.pools.append(db_pool)
            else:
                print('Knack Poll ID: {0} do not found in leica.'.format(kpool_id))
                msg = 'Knack Pool not found in Leica: {kpool_id}. ' \
                      'Professional name: {title} id: {professional_id}'
                logger.debug(msg.format(professional_id=obj.id, kpool_id=kpool_id, title=obj.title))

    def add_links(self, kobj, obj):
        """Add all professional links."""
        url = kobj.portfolio_web_site.url or ''
        # clean trash
        url = url.strip().lower()
        if 'testing.com' in url:
            url = ''
        elif '123.com' in url:
            url = ''
        elif 'Dumas' in url:
            url = 'http://www.bdumasonline.com/'
        elif 'bonis' in url:
            url = ''

        if not url:
            return

        url = url if url.startswith('http') else 'http://{url}'.format(url=url)
        # Use urlparse to get properly formatted urls
        o = urlparse(url)
        url = o.geturl()

        model = Portfolio
        if 'facebook.com' in url:
            model = Facebook
        elif 'flickr' in url:
            model = Flickr
        elif 'drive.google.com' in url:
            model = GDrive
        elif '500px' in url:
            model = FiveHundred
        elif 'linkedin' in url:
            model = Linkedin

        payload = {'professional_id': obj.id, 'url': url}
        try:
            link = model(**payload)
            self.session.add(link)
            self.session.flush()
        except Exception as error:
            msg = 'Failure to create link for Photorapher: {name}. Error: {error}'
            logger.error(msg.format(name=obj.first_name, error=error))

    def add(self, kobj, briefy_id):
        """Add new Photographer to database."""
        obj = super().add(kobj, briefy_id)
        self.add_locations(kobj, obj)
        self.add_links(kobj, obj)
        self.add_professional_pool(obj, kobj)
        return obj
