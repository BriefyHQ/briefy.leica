from briefy.leica import logger
from briefy.leica.models import MainWorkingLocation
from briefy.leica.models import AdditionalWorkingLocation
from briefy.leica.models import Photographer
from briefy.leica.sync import ModelSync
from briefy.leica.sync.location import create_location_dict

from sqlalchemy_utils import PhoneNumber


class PhotographerSync(ModelSync):
    """Syncronize Professionals."""

    model = Photographer
    knack_model_name = 'Photographer'

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
            msg = 'Failure to create location for Photorapher: {name}. Error: {error}'
            logger.error(msg.format(customer=obj.first_name, error=error))
        else:
            obj.locations.append(location)

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for a Professional object."""
        result = super().get_payload(kobj, briefy_id)

        first_name = kobj.display_name.first or 'first name'
        last_name = kobj.display_name.last or 'last name'
        main_mobile = kobj.phone.get('number') if kobj.phone else None
        location = create_location_dict('working_location_1', kobj)
        country = 'EMPTY'
        if location:
            country = location.get('country')

        if main_mobile:
            try:
                if main_mobile[:2] == '00':
                    print('Assuming international number: {0}. Country: {1}'.format(main_mobile,
                                                                                    country))
                    main_mobile = '+' + main_mobile[2:]
                elif main_mobile[:1] == '0':
                    if country == 'DE':
                        print('Assuming German number: {0}. Country: {1}'.format(main_mobile,
                                                                                 country))
                        main_mobile = '+49' + main_mobile[1:]
                elif len(main_mobile) > 11 and main_mobile[0] != '+':
                    print('Assuming international number: {0}. Country: {1}'.format(main_mobile,
                                                                                    country))
                    main_mobile = '+' + main_mobile

                main_mobile = PhoneNumber(main_mobile)
            except Exception as exc:
                msg = 'Briefy ID: {0} Number: {1}. Error: {2}'
                print(msg.format(kobj.briefy_id, main_mobile, exc))
                main_mobile = None

        result.update(
            dict(
                main_email=kobj.email.email or 'abc123@gmail.com',
                first_name=first_name,
                last_name=last_name,
                title='{0} {1}'.format(first_name, last_name),
                main_mobile=main_mobile
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

    def add(self, kobj, briefy_id):
        """Add new Photographer to database."""
        obj = super().add(kobj, briefy_id)
        self.add_locations(kobj, obj)
        return obj
