"""Test professionals view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestProfessionalView(BaseTestView):
    """Test ProfessionalService view."""

    base_path = '/professionals'
    dependencies = []
    file_path = 'data/professionals.json'
    model = models.Professional
    initial_wf_state = 'pending'
    serialize_attrs = ['path', '_roles', '_actors', 'intercom', 'main_location', 'locations']
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'description': 'Just another photographer',
        'messengers': {
            'skype': 'foo@bar.com'
        },
    }
    main_location_map = {
        'main_location':
            {
                'coordinates': [52.3758916, 9.732010400000036],
                'country': 'DE',
                'formatted_address': 'Hanover, Germany',
                'info': {
                    'coordinates': [52.3758916, 9.732010400000036],
                    'country': 'DE',
                    'formatted_address': 'Hanover, Germany',
                    'locality': 'Hanover',
                    'place_id': 'ChIJhU9JTVELsEcRIEeslG2sJQQ',
                    'postal_code': '',
                    'province': 'Lower Saxony',
                    'route': '',
                    'street_number': ''
                },
                'locality': 'Hanover'
            }
    }

    def test_successful_main_location_update(self, obj_payload, app):
        """Test creation and update of main_location of a Professional."""
        obj_id = obj_payload['id']
        updated_obj = self.model.get(obj_id)
        payload = self.main_location_map
        payload['main_location']['id'] = str(updated_obj._main_location.id)

        request = app.put_json('{base}/{id}'.format(base=self.base_path, id=obj_id),
                               payload, headers=self.headers, status=200)
        result = request.json
        assert 'application/json' == request.content_type
        assert updated_obj.main_location is not None
        assert updated_obj.main_location.country == result['main_location']['country']
        assert updated_obj.main_location.locality == result['main_location']['locality']

        # Update the same location
        payload['main_location']['id'] = str(updated_obj._main_location.id)
        payload['main_location']['info']['route'] = 'Brasilienstraße'

        request = app.put_json('{base}/{id}'.format(base=self.base_path, id=obj_id),
                               payload, headers=self.headers, status=200)
        result = request.json
        assert result['main_location']['info']['route'] == 'Brasilienstraße'
        assert result['main_location']['coordinates']['coordinates'][0] == 9.732010400000036
