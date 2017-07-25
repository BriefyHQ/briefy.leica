"""Test customers view."""
from briefy.leica import models
from conftest import BaseTestView


class TestCustomerView(BaseTestView):
    """Test CustomerService view."""

    base_path = '/customers'
    file_path = 'data/customers.json'
    model = models.Customer
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    initial_wf_state = 'pending'
    ignore_validation_fields = [
        'updated_at',
        'state',
        'state_history'
    ]
    update_map = {
        'title': 'New Customer Name',
        'description': 'New Customer Description',
    }

    def test_get_collection(self, app):
        """Test get a collection of items."""
        request = app.get(f'{self.base_path}', headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == len(result['data'])
        item = result['data'][0]
        assert 'legal_name' in item
        assert 'tax_country' in item
