"""Test Comment database model."""
from briefy.leica import models
from briefy.leica.events.comment import CommentCreatedEvent
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestCommentModel(BaseModelTest):
    """Test Comment."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Order, 'data/orders.json'),
        (models.Assignment, 'data/assignments.json'),
        (models.Image, 'data/images.json'),
    ]
    file_path = 'data/comments.json'
    model = models.Comment

    def test_to_dict_has_local_roles_from_entity(self, instance_obj, web_request):
        """Check if the event to_dict result has local roles attributes from the entity."""
        comment = instance_obj
        event = CommentCreatedEvent(comment, web_request)
        data = event.to_dict()
        entity_data = comment.entity.to_dict()
        assert data['_roles'] == entity_data['_roles']
        assert data['_actors'] == entity_data['_actors']
        assert data['entity'] == comment.entity.to_summary_dict()
