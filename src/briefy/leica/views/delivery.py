"""Views to handle Projects creation."""
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
            's3_path': '{client_id}/{project_id}/'}}
    ],

    'd466091b-98c5-4f9d-81a6-ecbc83dd3386': [
        {'gdrive': {
            'folder_structure': 'simple',
            'base_folder': 'https://drive.google.com/drive/folders/0BwrdIL719n7wVURQUC1VS2VKY0E',
            'sharing': ['erico@briefy.co'],
            'sets': [
                {
                    'folder_name': 'reduced_size',
                    'transforms': 'thumbor_filter',
                },
                {
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


@resource(path='/internal/jobs/{id}/delivery_info',
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
        if job is not None:
            assets = []
            for item in job.assets:
                assets.append(
                    dict(id=item.id,
                         source_path=item.source_path,
                         state=item.state)
                )
            result = {
                'job_id': job.id,
                'customer': job.project.customer_id,
                'customer_job_id': job.customer_job_id,
                'assets': assets,
                'settings': self.settings(job.project.customer_id)
            }
            return result

        else:
            self.request.response.status_code = 404
            return {
                'status': 'notfound',
                'message': 'Job not found.'
            }
