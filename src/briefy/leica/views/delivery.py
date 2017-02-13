"""Views to handle Delivery."""
from briefy.leica.config import AGODA_DELIVERY_GDRIVE
from briefy.leica.models import Assignment
from briefy.leica.views import InternalFactory
from briefy.ws import CORS_POLICY
from briefy.ws.resources.validation import validate_id
from cornice.resource import resource
from cornice.resource import view

import os

ENV = os.environ.get('ENV', 'staging')

DELIVERY_SETTINGS = {

    'default': [
        {'zip': {
            'filename': '{assignment_id}.zip',
            'folder_structure': 'simple',
            's3_bucket': 'delivery-{env}'.format(env=ENV),
            's3_path': '{client_id}/{project_id}/',
            'sets': [
                {
                    'id': 'original',
                    'folder_name': 'original',
                    'transforms': [],
                }
            ]
        }}
    ],

    'd466091b-98c5-4f9d-81a6-ecbc83dd3386': [
        {'gdrive': {
            'folder_structure': 'simple',
            'base_folder': AGODA_DELIVERY_GDRIVE,
            'sharing': [],
            'sets': [
                {
                    'id': 'reduced',
                    'folder_name': 'reduced_size',
                    'transforms': ['maxbytes(4000000)'],
                },
                {
                    'id': 'original',
                    'folder_name': 'original_size',
                    'transforms': '',
                }
            ]
        }}
    ]
}


class DeliveryFactory(InternalFactory):
    """Internal context factory for assignments delivery service."""

    model = Assignment


@resource(path='/internal/assignments/{id}/delivery',
          cors_policy=CORS_POLICY,
          factory=DeliveryFactory)
class DeliveryService:
    """Service to return delivery information to briefy.courier."""

    def __init__(self, context, request):
        """Service initialize."""
        self.context = context
        self.request = request

    @staticmethod
    def settings(customer_id):
        """Return settings for the current assignment/customer."""
        result = DELIVERY_SETTINGS.get(str(customer_id), None)
        if not result:
            result = DELIVERY_SETTINGS.get('default')
        return result

    def get_one(self):
        """Get one Assignment from the database."""
        assignment_id = self.request.matchdict.get('id')
        return Assignment.query().get(assignment_id)

    @view(permission='view', validators=[validate_id])
    def get(self):
        """Return user UUID from knack profile ID."""
        assignment = self.get_one()
        if assignment:
            approved_assets = []
            for item in assignment.assets:
                if item.state == item.workflow.approved.name:
                    approved_assets.append(
                        dict(id=item.id,
                             source_path=item.source_path,
                             state=item.state,
                             title=item.title,
                             )
                    )
            result = {
                'assignment_id': assignment.id,
                'customer': assignment.project.customer_id,
                'customer_assignment_id': assignment.customer_assignment_id,
                'assets': approved_assets,
                'settings': self.settings(assignment.project.customer_id)
            }
            return result

        else:
            self.request.response.status_code = 404
            return {
                'status': 'notfound',
                'message': 'Assignment not found.'
            }

    @view(permission='edit', validators=[validate_id])
    def put(self):
        """Update delivery link after briefy.courier build the delivey package."""
        assignment = self.get_one()
        if assignment:
            pass
        else:
            self.request.response.status_code = 404
            return {
                'status': 'notfound',
                'message': 'Assignment not found.'
            }
