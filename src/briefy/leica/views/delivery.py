"""Views to handle Projects creation."""
from briefy.leica.config import AGODA_DELIVERY_GDRIVE
from briefy.leica.models import Job
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
            'filename': '{job_id}.zip',
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


class DeliveryInfoFactory(InternalFactory):
    """Internal context factory for jobs delivery service."""

    model = Job


@resource(path='/internal/jobs/{id}/delivery',
          cors_policy=CORS_POLICY,
          factory=DeliveryInfoFactory)
class DeliveryInfoService:
    """Service to return delivery information to briefy.courrier."""

    def __init__(self, context, request):
        """Service initialize."""
        self.context = context
        self.request = request

    @staticmethod
    def settings(customer_id):
        """Return settings for the current job/customer."""
        result = DELIVERY_SETTINGS.get(str(customer_id), None)
        if not result:
            return DELIVERY_SETTINGS.get('default')
        else:
            return result

    def get_one(self):
        """Get on Job from the database."""
        job_id = self.request.matchdict.get('id')
        return Job.query().get(job_id)

    @view(permission='view',
          validators=[validate_id])
    def get(self):
        """Return user UUID from knack profile ID."""
        job = self.get_one()
        if job:
            approved_assets = []
            for item in job.assets:
                if item.state == item.workflow.approved.name:
                    approved_assets.append(
                        dict(id=item.id,
                             source_path=item.source_path,
                             state=item.state,
                             title=item.title,
                             )
                    )
            result = {
                'job_id': job.id,
                'customer': job.project.customer_id,
                'customer_job_id': job.customer_job_id,
                'assets': approved_assets,
                'settings': self.settings(job.project.customer_id)
            }
            return result

        else:
            self.request.response.status_code = 404
            return {
                'status': 'notfound',
                'message': 'Job not found.'
            }
