"""Test customers view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest
import uuid


LISTING_FILTERS_PAYLOADS = [
    ({'ilike_legal_name': 'Delivery',
      'tax_country': 'DE',
      'customer_id': 'c2034c1b-0a40-4b84-9ace-54b958f64ed4'}, 1),
    ({'ilike_legal_name': 'Agoda',
      'tax_country': 'SG',
      'customer_id': 'f61437ce-ca13-4a64-8474-c43906267215'}, 1),
    ({'tax_country': 'SG',
      'customer_id': '51eaab79-1c05-44fa-b3cf-278ecf311978'}, 2)
]


@pytest.mark.usefixtures('create_dependencies')
class TestCustomerView(BaseTestView):
    """Test CustomerService view."""

    base_path = '/customers'
    dependencies = [
        (models.Customer, 'data/customers.json'),
    ]
    file_path = 'data/customers.json'
    model = models.Customer
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    initial_wf_state = 'pending'
    update_map = {
        'title': 'New Customer Name',
        'description': 'New Customer Description',
    }

    @pytest.mark.parametrize('file_path, position', [('data/customer_billing_infos.json', 0)])
    @pytest.mark.parametrize('filter_payload, total', LISTING_FILTERS_PAYLOADS)
    def test_collection_get_with_filters(self, app, get_file_payload, filter_payload, total):
        """Test collection_get endpoint with special filters."""
        customer = self.model.get(filter_payload.pop('customer_id'))
        country = filter_payload.get('tax_country')
        legal_name = filter_payload.get('ilike_legal_name', 'Company')
        billing_info_payload = get_file_payload
        billing_info_payload['id'] = uuid.uuid4()
        billing_info_payload['title'] = f'The {legal_name} Inc.'
        billing_info_payload['billing_address']['country'] = country
        billing_info_payload['customer_id'] = customer.id

        # create new billing info instance
        models.CustomerBillingInfo.create(billing_info_payload)

        base_path = self.get_base_path_with_query_str(filter_payload)
        request = app.get(base_path, headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == len(result['data']) == total
