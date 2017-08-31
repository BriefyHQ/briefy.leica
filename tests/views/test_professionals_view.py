"""Test professionals view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


LISTING_FILTERS_PAYLOADS = [
    ({'like_main_location.country': 'DE',
      'ilike_main_location.locality': 'Hanover',
      'ilike_title': 'salgado',
      'ilike_email': 'professional.briefy.co'}, 1),
]


@pytest.mark.usefixtures('create_dependencies')
class TestProfessionalView(BaseTestView):
    """Test ProfessionalService view."""

    base_path = '/professionals'
    file_path = 'data/professionals.json'
    model = models.Professional
    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]
    initial_wf_state = 'pending'
    serialize_attrs = [
        'path', '_roles', '_actors', 'intercom'
    ]
    ignore_validation_fields = [
        'state_history', 'state', 'locations', 'main_location', 'links'
    ]
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'description': 'Just another photographer',
        'messengers': {
            'skype': 'foo@bar.com'
        }
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
        """Test update of the Professional main_location."""
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

    def test_successful_links_update(self, obj_payload, app):
        """Test update of the Professional links."""
        obj_id = obj_payload['id']
        updated_obj = self.model.get(obj_id)
        links = updated_obj.links
        assert len(links) == 2
        update_link = links[0]

        payload = {
            'links': [{
                'id': update_link.id,
                'type': update_link.type,
                'url': 'https://url.com',
                'state': update_link.state
            }]
        }
        request = app.put_json('{base}/{id}'.format(base=self.base_path, id=obj_id),
                               payload, headers=self.headers, status=200)
        result = request.json
        assert 'application/json' == request.content_type

        assert 'links' in result.keys()
        obj_results = result.get('links')
        assert len(obj_results) == 1
        obj_result = obj_results[0]
        result_keys = list(obj_result.keys())
        result_values = list(obj_result.values())

        for key, value in payload.get('links')[0].items():
            assert key in result_keys
            assert str(value) in result_values

        updated_obj = self.model.get(obj_id)
        assert updated_obj.links is not None
        assert len(updated_obj.links) == 1

    @pytest.mark.parametrize('file_path, position', [('data/professionals.json', 0)])
    @pytest.mark.parametrize('filter_payload, total', LISTING_FILTERS_PAYLOADS)
    def test_collection_get_with_filters(self, app, get_file_payload, filter_payload, total):
        """Test collection_get endpoint with special filters."""
        professional_payload = get_file_payload
        location_payload = professional_payload['main_location']
        location_payload.pop('latlng')
        # create new main working location instance
        models.MainWorkingLocation.create(location_payload)

        base_path = self.get_base_path_with_query_str(filter_payload)
        request = app.get(base_path, headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == len(result['data']) == total
