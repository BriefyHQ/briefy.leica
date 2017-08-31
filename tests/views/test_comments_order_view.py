"""Test Order comments view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestOrderComments(BaseTestView):
    """Test Comments for an order."""

    base_path = '/orders/011418fa-f450-4deb-b6ea-7f8e103a66d1/comments'
    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Order, 'data/orders.json'),
        (models.Assignment, 'data/assignments.json'),
        (models.Image, 'data/images.json')
    ]
    file_path = 'data/comments.json'
    model = models.Comment
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    payload_position = 10
    update_map = {
        'content': 'new message content',
        'author_id': '18d0e257-14d6-4e33-b873-fb506fffb42e',
    }

    def test_get_collection_count(self, app):
        """Test get a collection of items."""
        request = app.get(f'{self.base_path}', headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == len(result['data'])
        assert result['total'] == 1

    def test_get_collection_as_customer(self, app, obj_payload, login_as_customer):
        """Test get a collection of Comments for the order as a customer.

        Should ignore internal comments.
        """
        # Update comment to be internal
        obj_id = obj_payload['id']
        payload = {'internal': True}
        headers = {k: v for k, v in self.headers.items()}
        app.put_json(f'{self.base_path}/{obj_id}', payload, headers=headers, status=200)
        # Now log as customer
        user_payload, token = login_as_customer
        headers['Authorization'] = f'JWT {token}'
        request = app.get(f'{self.base_path}', headers=headers, status=200)
        result = request.json
        assert result['total'] == len(result['data'])
        assert result['total'] == 0
